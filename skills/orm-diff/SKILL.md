---
name: orm-diff
description: "扫描 projects/vpp/shandong/models 目录下所有 SQLAlchemy ORM 模型，连接数据库读取对应表的实际结构，全属性对比差异（列名、类型、nullable、default、primary_key），输出控制台表格报告。当用户提到 ORM 对比、模型差异、表结构变化、数据库迁移检查、schema diff、模型与数据库不一致时触发。"
---

# ORM-DB 表结构对比技能

扫描 `projects/vpp/shandong/models/` 下所有 ORM 模型，与数据库实际表结构做全属性对比，找出差异。

## 使用方式

运行脚本：

```bash
python .agent/skills/orm-diff/scripts/orm_diff.py
```

脚本会：
1. 自动发现 models 目录下所有继承 `Base` 的 ORM 类
2. 连接数据库（使用 `projects.vpp.shandong.mconfig` 中的同步连接串 `DB_URL`）
3. 读取每张表的实际列信息（`information_schema.columns`）
4. 逐列对比：列名是否存在、数据类型、nullable、default、primary_key
5. 输出控制台表格报告

## 输出格式

### 无差异时

```
✓ mgems_vpp_energy_bid — 一致 (12 列)
✓ mgems_def_vpp — 一致 (14 列)
```

### 有差异时

```
✗ mgems_vpp_energy_bid — 3 处差异
  ORM 缺失列:
    DB: NEW_COL  varchar(64)  nullable=YES  default=NULL

  DB 缺失列:
    ORM: quote_strategy  String(32)  nullable=True  default=None

  属性不一致:
    PRICE: type ORM=Float vs DB=numeric(10,2)
    STATUS: nullable ORM=True vs DB=False
```

### 汇总

```
──────────────────────────────────
总计: 15 张表, 12 一致, 3 有差异
──────────────────────────────────
```

## 对比维度

| 属性 | ORM 来源 | DB 来源 |
|------|---------|---------|
| 列名 | `Column('NAME', ...)` | `information_schema.columns.column_name` |
| 数据类型 | SQLAlchemy 类型映射 | `udt_name` + `character_maximum_length` 等 |
| nullable | `Column(nullable=...)` | `is_nullable` |
| default | `Column(default=...)` / `server_default` | `column_default` |
| primary_key | `Column(primary_key=True)` | `pg_constraint` 查询 |

## 特殊处理

- `ts_column()` 工厂函数产生的列：ORM 侧类型为 `_UnixTimestamp`（底层 `BigInteger`），对比时按 `BigInteger` ↔ `bigint` 匹配
- `__table_args__` 中的 `extend_existing=True` 不影响对比
- `autoincrement` 属性不纳入对比（PostgreSQL 的 SERIAL/IDENTITY 隐式处理）
- `comment` 属性不纳入对比（仅作参考，不影响结构）

## 环境要求

- Python 3.11+
- 依赖：`sqlalchemy`, `psycopg2`（同步驱动）
- 数据库连接配置来自 `projects.vpp.shandong.mconfig.DB_URL`
- 需要数据库网络可达（连接配置来自 mconfig）
