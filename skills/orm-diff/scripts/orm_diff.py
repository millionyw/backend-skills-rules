"""ORM 模型 vs 数据库表结构全属性对比工具

扫描 projects/vpp/shandong/models/ 下所有继承 Base 的 ORM 类，
连接 PostgreSQL 读取实际表结构，逐列全属性对比并输出差异报告。

用法:
    python .agent/skills/orm-diff/scripts/orm_diff.py
"""

import importlib
import os
import pkgutil
import sys
from collections import OrderedDict
from typing import Any

# Windows 控制台 UTF-8 输出
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
# scripts/ → orm-diff/ → skills/ → .agent/ → rtdbpy_04/  (4 层)
sys.path.append(os.path.join(CUR_PATH, '../../../..'))

import psycopg2

from projects.vpp.shandong.mconfig import DB_URL

# SQLAlchemy 类型 → PostgreSQL 类型简称的映射（用于对比）
_SA_TO_PG_SIMPLE: dict[str, str] = {
    'INTEGER': 'int4',
    'BIGINT': 'int8',
    'SMALLINT': 'int2',
    'FLOAT': 'float8',
    'REAL': 'float4',
    'NUMERIC': 'numeric',
    'VARCHAR': 'varchar',
    'CHAR': 'bpchar',
    'TEXT': 'text',
    'BOOLEAN': 'bool',
    'DATE': 'date',
    'TIME': 'time',
    'TIMESTAMP': 'timestamp',
    'BYTEA': 'bytea',
}


def _sa_type_to_pg(sa_type: Any) -> str:
    """将 SQLAlchemy 列类型转换为 PostgreSQL 类型简称（小写）。"""
    # 自定义类型 _UnixTimestamp 底层是 BigInteger
    type_cls = type(sa_type)
    if type_cls.__name__ == '_UnixTimestamp':
        return 'int8'

    type_name = type(sa_type).__name__.upper()

    # String → varchar
    if type_name == 'STRING':
        length = getattr(sa_type, 'length', None)
        return f'varchar({length})' if length else 'varchar'
    # Integer 系列
    if type_name == 'INTEGER':
        return 'int4'
    if type_name == 'BIGINTEGER':
        return 'int8'
    if type_name == 'SMALLINTEGER':
        return 'int2'
    # Float / Float(precision)
    if type_name == 'FLOAT':
        return 'float8'
    # Numeric(asdecimal=...)
    if type_name == 'NUMERIC':
        p = getattr(sa_type, 'precision', None)
        s = getattr(sa_type, 'scale', None)
        if p and s is not None:
            return f'numeric({p},{s})'
        return 'numeric'
    # Date
    if type_name == 'DATE':
        return 'date'

    # 通用映射
    return _SA_TO_PG_SIMPLE.get(type_name, type_name.lower())


def _pg_type_display(udt_name: str, char_len: int | None, numeric_precision: int | None,
                     numeric_scale: int | None) -> str:
    """将 information_schema 字段拼成可读类型字符串。"""
    udt = udt_name.lower()
    if udt in ('varchar', 'bpchar') and char_len:
        return f'{udt}({char_len})'
    if udt == 'numeric' and numeric_precision is not None:
        if numeric_scale is not None:
            return f'numeric({numeric_precision},{numeric_scale})'
        return f'numeric({numeric_precision})'
    return udt


def _types_compatible(sa_pg: str, db_pg: str) -> bool:
    """判断 ORM 类型与 DB 类型是否兼容。

    int4/int8 之间、float4/float8 之间、varchar 不同长度之间视为兼容
    （ORM 声明 Integer 但 DB 是 bigint 是常见情况，不报告为差异）。
    """
    # 完全一致
    if sa_pg == db_pg:
        return True

    # 去掉括号部分比较基类型
    sa_base = sa_pg.split('(')[0]
    db_base = db_pg.split('(')[0]

    # 整数族互通
    int_types = {'int2', 'int4', 'int8'}
    if sa_base in int_types and db_base in int_types:
        return True

    # 浮点族互通
    float_types = {'float4', 'float8', 'numeric'}
    if sa_base in float_types and db_base in float_types:
        return True

    # varchar/bpchar/text 互通
    str_types = {'varchar', 'bpchar', 'text'}
    if sa_base in str_types and db_base in str_types:
        return True

    return False


def _discover_models() -> list[tuple[str, Any]]:
    """自动发现 models 包下所有继承 Base 的 ORM 类。

    返回: [(表名, ORM类), ...]
    """
    import projects.vpp.shandong.models as models_pkg
    from projects.vpp.shandong.models import Base

    results: list[tuple[str, Any]] = []
    pkg_path = os.path.dirname(models_pkg.__file__)

    for _importer, mod_name, _ispkg in pkgutil.iter_modules([pkg_path]):
        if mod_name.startswith('_'):
            continue
        mod = importlib.import_module(f'projects.vpp.shandong.models.{mod_name}')
        for attr_name in dir(mod):
            obj = getattr(mod, attr_name)
            if (isinstance(obj, type)
                    and issubclass(obj, Base)
                    and obj is not Base
                    and hasattr(obj, '__tablename__')):
                results.append((obj.__tablename__, obj))

    return sorted(results, key=lambda x: x[0])


def _fetch_db_columns(conn: psycopg2.extensions.connection, table_name: str) -> dict[str, dict]:
    """从 information_schema + pg_constraint 读取表的实际列信息。

    返回: {列名大写: {type, nullable, default, is_pk}, ...}
    """
    cur = conn.cursor()

    # 获取列基本信息
    cur.execute("""
        SELECT column_name, udt_name, character_maximum_length,
               numeric_precision, numeric_scale,
               is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
          AND table_schema = 'public'
        ORDER BY ordinal_position
    """, (table_name,))

    columns: dict[str, dict] = {}
    for row in cur.fetchall():
        col_name, udt_name, char_len, num_prec, num_scale, is_nullable, col_default = row
        columns[col_name.upper()] = {
            'type': _pg_type_display(udt_name, char_len, num_prec, num_scale),
            'udt_name': udt_name.lower(),
            'nullable': is_nullable == 'YES',
            'default': col_default,
        }

    # 获取主键列
    cur.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_name = %s
          AND tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'
    """, (table_name,))
    pk_cols = {row[0].upper() for row in cur.fetchall()}
    for col_name in pk_cols:
        if col_name in columns:
            columns[col_name]['is_pk'] = True

    cur.close()
    return columns


def _extract_orm_columns(orm_cls: Any) -> dict[str, dict]:
    """从 ORM 类提取列定义信息。

    返回: {列名大写: {type, nullable, default, is_pk}, ...}
    """
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(orm_cls)
    columns: dict[str, dict] = {}

    for col in mapper.columns:
        col_name = col.name.upper()
        sa_type_str = _sa_type_to_pg(col.type)

        # default 处理
        default_val = None
        if col.default is not None:
            default_val = col.default.arg
        elif col.server_default is not None:
            default_val = str(col.server_default.arg)

        columns[col_name] = {
            'type': sa_type_str,
            'nullable': col.nullable,
            'default': default_val,
            'is_pk': col.primary_key,
        }

    return columns


def _compare_table(orm_cls: Any, db_cols: dict[str, dict]) -> list[str]:
    """对比单个 ORM 类与数据库表，返回差异描述列表。"""
    orm_cols = _extract_orm_columns(orm_cls)
    diffs: list[str] = []

    orm_names = set(orm_cols.keys())
    db_names = set(db_cols.keys())

    # ORM 有但 DB 没有
    orm_only = orm_names - db_names
    if orm_only:
        for name in sorted(orm_only):
            c = orm_cols[name]
            diffs.append(
                f"  ORM 有 / DB 缺失: {name}  {c['type']}  "
                f"nullable={c['nullable']}  default={c['default']}"
            )

    # DB 有但 ORM 没有
    db_only = db_names - orm_names
    if db_only:
        for name in sorted(db_only):
            c = db_cols[name]
            diffs.append(
                f"  DB 有 / ORM 缺失: {name}  {c['type']}  "
                f"nullable={c['nullable']}  default={c['default']}"
            )

    # 共有列的属性对比
    common = orm_names & db_names
    for name in sorted(common):
        oc = orm_cols[name]
        dc = db_cols[name]
        attr_diffs: list[str] = []

        # 类型对比
        if not _types_compatible(oc['type'], dc['type']):
            attr_diffs.append(f"type: ORM={oc['type']} vs DB={dc['type']}")

        # nullable 对比
        if oc['nullable'] != dc['nullable']:
            attr_diffs.append(f"nullable: ORM={oc['nullable']} vs DB={dc['nullable']}")

        # primary_key 对比
        orm_pk = oc.get('is_pk', False)
        db_pk = dc.get('is_pk', False)
        if orm_pk != db_pk:
            attr_diffs.append(f"primary_key: ORM={orm_pk} vs DB={db_pk}")

        # default 对比（仅当 ORM 显式声明了 default 时才比较，避免误报）
        if oc['default'] is not None:
            orm_def = str(oc['default'])
            db_def = str(dc['default']) if dc['default'] is not None else 'NULL'
            # 归一化：去除类型转换前缀如 '0'::integer → '0'
            db_def_clean = db_def.split('::')[0].strip("'")
            if orm_def != db_def_clean and orm_def != db_def:
                attr_diffs.append(f"default: ORM={orm_def} vs DB={db_def}")

        if attr_diffs:
            diffs.append(f"  属性不一致 [{name}]: {'; '.join(attr_diffs)}")

    return diffs


def main():
    models = _discover_models()
    if not models:
        print('未发现任何 ORM 模型')
        return

    print(f'发现 {len(models)} 个 ORM 模型，正在连接数据库...\n')

    conn = psycopg2.connect(DB_URL)
    try:
        ok_count = 0
        diff_count = 0
        missing_tables: list[str] = []

        for table_name, orm_cls in models:
            db_cols = _fetch_db_columns(conn, table_name)

            if not db_cols:
                missing_tables.append(table_name)
                print(f'✗ {table_name} — 数据库中不存在')
                diff_count += 1
                continue

            diffs = _compare_table(orm_cls, db_cols)
            col_count = len(_extract_orm_columns(orm_cls))

            if not diffs:
                print(f'✓ {table_name} — 一致 ({col_count} 列)')
                ok_count += 1
            else:
                print(f'✗ {table_name} — {len(diffs)} 处差异')
                for d in diffs:
                    print(d)
                print()
                diff_count += 1

        # 汇总
        print('─' * 50)
        print(f'总计: {len(models)} 张表, '
              f'{ok_count} 一致, '
              f'{diff_count} 有差异', end='')
        if missing_tables:
            print(f' (其中 {len(missing_tables)} 张表在 DB 中不存在)')
        else:
            print()
        print('─' * 50)

    finally:
        conn.close()


if __name__ == '__main__':
    main()
