---
name: json-canvas
description: Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use this skill whenever the user wants to create, edit, or work with Obsidian JSON Canvas files including nodes, edges, groups, and visual layouts.
---

# JSON Canvas Skill

This skill enables you to create and edit JSON Canvas (.canvas) files for Obsidian. Canvas is a visual whiteboarding feature in Obsidian that lets you arrange nodes (notes, images, text) on an infinite canvas and connect them with edges.

## Quick Reference

```json
{
  "nodes": [
    {
      "id": "node-id",
      "type": "text",
      "text": "Node content",
      "x": 0,
      "y": 0,
      "width": 200,
      "height": 100
    }
  ],
  "edges": [
    {
      "id": "edge-id",
      "fromNode": "node-1",
      "fromSide": "right",
      "toNode": "node-2",
      "toSide": "left"
    }
  ]
}
```

## Canvas File Format

Canvas files use the `.canvas` extension and are stored as JSON. They contain:

- `nodes` — Array of node objects
- `edges` — Array of edge (connection) objects
- `groupColors` — Optional array of color definitions for groups

## Node Types

| Type | Description |
| ---- | ----------- |
| `text` | Text/markdown content |
| `file` | Reference to a file in your vault |
| `link` | External URL link |
| `image` | Image from vault or external URL |
| `group` | Container for grouping nodes |

### Text Node

```json
{
  "id": "text-1",
  "type": "text",
  "text": "# Hello\n\nThis is a text node with **markdown** support.",
  "x": 0,
  "y": 0,
  "width": 300,
  "height": 200
}
```

### File Node

```json
{
  "id": "file-1",
  "type": "file",
  "file": "Notes/My Note.md",
  "x": 100,
  "y": 100,
  "width": 250,
  "height": 300
}
```

### Link Node

```json
{
  "id": "link-1",
  "type": "link",
  "url": "https://obsidian.md",
  "title": "Obsidian Website",
  "x": 200,
  "y": 200,
  "width": 200,
  "height": 100
}
```

### Image Node

```json
{
  "id": "image-1",
  "type": "image",
  "url": "attachment://diagram.png",
  "x": 300,
  "y": 300,
  "width": 400,
  "height": 300
}
```

### Group Node

```json
{
  "id": "group-1",
  "type": "group",
  "children": ["node-1", "node-2"],
  "x": 0,
  "y": 0,
  "width": 600,
  "height": 400,
  "color": "#ff0000"
}
```

## Node Properties

| Property | Type | Description |
| -------- | ---- | ----------- |
| `id` | string | Unique identifier for the node |
| `type` | string | Type of node: text, file, link, image, group |
| `x` | number | X position on canvas |
| `y` | number | Y position on canvas |
| `width` | number | Width of the node |
| `height` | number | Height of the node |
| `text` | string | Content for text nodes (markdown supported) |
| `file` | string | Path to file for file nodes |
| `url` | string | URL for link/image nodes |
| `title` | string | Title for link nodes |
| `children` | array | Array of child node IDs for groups |
| `color` | string | Color for group nodes |

## Edge Types

Edges connect nodes together. There are basic edges and advanced edges with specific endpoints.

### Basic Edge

```json
{
  "id": "edge-1",
  "fromNode": "node-1",
  "toNode": "node-2"
}
```

### Advanced Edge with Side

```json
{
  "id": "edge-1",
  "fromNode": "node-1",
  "fromSide": "right",
  "toNode": "node-2",
  "toSide": "left"
}
```

### Edge with Specific Endpoint

```json
{
  "id": "edge-1",
  "fromNode": "node-1",
  "fromSide": "bottom",
  "fromEnd": "none",
  "toNode": "node-2",
  "toSide": "top",
  "toEnd": "arrow"
}
```

## Edge Properties

| Property | Type | Description |
| -------- | ---- | ----------- |
| `id` | string | Unique identifier for the edge |
| `fromNode` | string | ID of the source node |
| `fromSide` | string | Side of source node: top, right, bottom, left |
| `fromEnd` | string | End style for source: arrow, none |
| `toNode` | string | ID of the target node |
| `toSide` | string | Side of target node: top, right, bottom, left |
| `toEnd` | string | End style for target: arrow, none |

### Side Values

- `top` — Top edge of the node
- `right` — Right edge of the node
- `bottom` — Bottom edge of the node
- `left` — Left edge of the node

### End Values

- `arrow` — Arrow head (default)
- `none` — No arrow head

## Groups

Groups are containers that hold multiple nodes and can have a background color.

```json
{
  "id": "group-1",
  "type": "group",
  "children": ["node-1", "node-2", "node-3"],
  "x": 0,
  "y": 0,
  "width": 800,
  "height": 600,
  "color": "#3b82f6"
}
```

### Group Properties

| Property | Type | Description |
| -------- | ---- | ----------- |
| `id` | string | Unique identifier |
| `type` | string | Must be "group" |
| `children` | array | Array of node IDs to include |
| `x` | number | X position |
| `y` | number | Y position |
| `width` | number | Width of the group |
| `height` | number | Height of the group |
| `color` | string | Background color (hex or CSS color name) |

## Complete Example

```json
{
  "nodes": [
    {
      "id": "welcome",
      "type": "text",
      "text": "# Welcome\n\nThis canvas demonstrates the structure.",
      "x": 0,
      "y": 0,
      "width": 300,
      "height": 200
    },
    {
      "id": "features",
      "type": "text",
      "text": "## Features\n\n- Text nodes\n- File nodes\n- Images\n- Connections",
      "x": 400,
      "y": 0,
      "width": 250,
      "height": 200
    },
    {
      "id": "image-node",
      "type": "image",
      "url": "attachment://diagram.png",
      "x": 200,
      "y": 250,
      "width": 300,
      "height": 200
    },
    {
      "id": "link-node",
      "type": "link",
      "url": "https://obsidian.md",
      "title": "Learn More",
      "x": 600,
      "y": 250,
      "width": 200,
      "height": 100
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "fromNode": "welcome",
      "fromSide": "right",
      "toNode": "features",
      "toSide": "left"
    },
    {
      "id": "edge-2",
      "fromNode": "welcome",
      "fromSide": "bottom",
      "toNode": "image-node",
      "toSide": "top"
    },
    {
      "id": "edge-3",
      "fromNode": "features",
      "fromSide": "bottom",
      "toNode": "link-node",
      "toSide": "top"
    }
  ],
  "groupColors": [
    {
      "color": "#3b82f6",
      "text": "blue"
    }
  ]
}
```

## Best Practices

1. **Use unique IDs** — Each node and edge should have a unique ID (use UUIDs or descriptive names)
2. **Position thoughtfully** — Place related nodes near each other and use consistent spacing
3. **Connect logically** — Use edges to show relationships between nodes
4. **Use groups** — Group related nodes together for visual organization
5. **Add colors** — Use group colors to categorize and visually distinguish sections
6. **Include text nodes as labels** — Use text nodes to label and explain connections
7. **Test in Obsidian** — Canvas files work best when tested in the Obsidian app

## Markdown in Text Nodes

Text nodes support full Obsidian markdown:

```json
{
  "id": "formatted",
  "type": "text",
  "text": "# Heading\n\n**Bold** and *italic*\n\n- List item 1\n- List item 2\n\n[[Wiki Link]]\n\n> [!note]\n> Callout text\n\n```\ncode block\n```"
}
```
