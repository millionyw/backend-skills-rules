---
name: obsidian-bases
description: Create and edit Obsidian Bases (.base) with views, filters, formulas, and summaries. Use this skill whenever the user wants to create, edit, or work with Obsidian Bases database files including tables, views, filters, formulas, and data aggregation.
---

# Obsidian Bases Skill

This skill enables you to create and edit Obsidian Bases (.base) files. Obsidian Bases is a database system for Obsidian that uses YAML-based files to define database schemas with properties, views, filters, formulas, and summaries.

## Quick Reference

```yaml
---
base: Base Name
columns:
  - name: Property Name
    type: text
views:
  - name: View Name
    type: table
properties:
  Property Name:
    type: text
---
```

## Base Files

Bases are stored in `.base` files which are YAML files with a specific structure:

- `base` — The name of the database
- `columns` — Array of column definitions
- `views` — Array of view definitions
- `properties` — Property type definitions

## Column Types

| Type | Description | Example |
| ---- | ----------- | ------- |
| `text` | Plain text | `name: Title` |
| `number` | Numeric values | `name: Price` |
| `select` | Single select from options | `name: Status` |
| `multiselect` | Multiple select options | `name: Tags` |
| `checkbox` | True/false values | `name: Done` |
| `date` | Date values | `name: Due Date` |
| `daterange` | Date ranges | `name: Period` |
| `person` | Obsidian users | `name: Owner` |
| `file` | File references | `name: Attachment` |
| `url` | URLs | `name: Link` |
| `email` | Email addresses | `name: Contact` |
| `phone` | Phone numbers | `name: Phone` |
| `formula` | Calculated values | `name: Total` |
| `relation` | Links to other bases | `name: Related` |

## Views

Views define how data is displayed. The main view types are:

### Table View

```yaml
views:
  - name: Table View
    type: table
    columns:
      - name: Property Name
        width: 200
        align: left
```

### Board View

```yaml
views:
  - name: Kanban Board
    type: board
    groupBy: Status
```

### Gallery View

```yaml
views:
  - name: Gallery
    type: gallery
    image: Cover
    title: Title
    size: medium
```

### Calendar View

```yaml
views:
  - name: Calendar
    type: calendar
    date: Due Date
```

## Filters

Filters define which rows are shown in a view:

```yaml
filters:
  - property: Status
    operator: ==
    value: Active
  - property: Due Date
    operator: <
    value: today
```

### Filter Operators

| Operator | Description |
| -------- | ----------- |
| `==` | Equals |
| `!=` | Not equals |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater or equal |
| `<=` | Less or equal |
| `contains` | Contains substring |
| `starts_with` | Starts with |
| `ends_with` | Ends with |
| `is_empty` | Is empty |
| `is_not_empty` | Is not empty |

## Formulas

Formulas calculate values based on other properties:

```yaml
- name: Total
  type: formula
  formula: price * quantity
  options:
    precision: 2
```

### Formula Functions

See the [Functions Reference](./references/FUNCTIONS_REFERENCE.md) for a complete list of available functions.

### Common Functions

| Function | Description | Example |
| -------- | ----------- | ------- |
| `sum()` | Sum of values | `sum(items)` |
| `avg()` | Average value | `avg(scores)` |
| `count()` | Count of items | `count(tasks)` |
| `min()` | Minimum value | `min(prices)` |
| `max()` | Maximum value | `max(prices)` |
| `if()` | Conditional | `if(status == "done", "Yes", "No")` |
| `concat()` | Concatenate strings | `concat(first, " ", last)` |
| `length()` | String length | `length(name)` |
| `round()` | Round number | `round(price, 2)` |

## Summaries

Summaries aggregate data across views:

```yaml
summaries:
  - name: Total Tasks
    function: count
    source: tasks
  - name: Average Score
    function: avg
    source: scores
```

### Summary Functions

| Function | Description |
| -------- | ----------- |
| `count` | Count of items |
| `sum` | Sum of values |
| `avg` | Average value |
| `min` | Minimum value |
| `max` | Maximum value |
| `array` | Array of values |

## Properties Configuration

Define property types and options:

```yaml
properties:
  Title:
    type: text
  Status:
    type: select
    options:
      - To Do
      - In Progress
      - Done
  Tags:
    type: multiselect
    options:
      - Important
      - Urgent
      - Review
  Due Date:
    type: date
  Completed:
    type: checkbox
```

## Best Practices

1. **Use appropriate column types** — Choose the right type for your data (e.g., use `date` for dates, `select` for limited options)
2. **Define views for different needs** — Create table, board, gallery, and calendar views for different ways of viewing your data
3. **Use filters to segment data** — Create filtered views for different use cases
4. **Use formulas for calculations** — Keep your data DRY by calculating values instead of manually entering them
5. **Use summaries for aggregations** — Aggregate data across your base for insights
6. **Keep properties consistent** — Use the same property names and types across your bases
7. **Document your schema** — Add comments or documentation to explain complex formulas or relationships
