---
name: obsidian-markdown
description: Create and edit Obsidian Flavored Markdown (.md) with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use this skill whenever the user wants to create, edit, or work with Obsidian markdown files, including notes with YAML frontmatter, wikilinks [[like this]], embeds ![[like this]], callouts (> [!note]), and Obsidian properties (key: value).
---

# Obsidian Markdown Skill

This skill enables you to create and edit Obsidian Flavored Markdown (OFM) for use in Obsidian vaults. The skill covers the following core competencies:

1. **YAML frontmatter** — Also known as properties, these live at the top of the file between `---` fences
2. **Wikilinks** — Internal links `[[like this]]` that link to other notes in the vault
3. **Embeds** — Embed content from other notes `![[like this]]`
4. **Callouts** — Callout blocks `> [!note]` for highlighting content
5. **Markdown syntax** — Standard markdown like **bold**, *italic*, `code`, and [links](url)

## YAML Frontmatter

Use YAML frontmatter (also known as **properties**) to add metadata to your notes. Place them at the very top of your file, between two lines of three dashes `---`.

### Quick Reference

```
---
alias: Person
tags: [person, important]
cssclass: table-full-width
---
```

### Properties Best Practices

- Use lowercase for property keys like `tags:`, `alias:`, `date:`
- Use arrays `[tag1, tag2]` for multi-value properties like tags
- Use camelCase or snake_case for multi-word property values
- Put the `---` closing fence on its own line
- Always put properties at the very top of the file, before any other content
- Obsidian supports [various property types](https://help.obsidian.md/Editing+and+formatting/Properties#Property+types) including text, list, number, checkbox, date, date+time, and select

### Common Properties

| Property | Description | Example |
| -------- | ----------- | ------- |
| `title` | The display title of the note | `title: My Note` |
| `alias` | Alternative names for the note (use `aliases` for multiple) | `alias: [Note, Note Name]` |
| `tags` | Tags for categorizing the note | `tags: [work, project, important]` |
| `date` | A date in `YYYY-MM-DD` format | `date: 2024-01-15` |
| `type` | The type of note | `type: literature-note` |
| `cssclass` | Custom CSS classes to apply to the note | `cssclass: table-max-width` |

### Example

```
---
title: Project Phoenix
alias: [Phoenix, Project Phoenix]
tags: [work, active, q1-2024]
date: 2024-01-15
type: project
cssclass: table-full-width
---

# Project Phoenix

This is the start of the note content...
```

## Wikilinks

Wikilinks are the internal linking syntax in Obsidian. They link to other notes in your vault.

### Quick Reference

```
[[Note Name]]
[[Note Name|Display Text]]
```

### Wikilink Syntax

- **Basic link:** `[[Note Name]]` — Links to a note called "Note Name"
- **Link with display text:** `[[Note Name|Display Text]]` — Displays "Display Text" but links to "Note Name"
- **Link to heading:** `[[Note Name#Heading]]` — Links to a specific heading in the note
- **Link to block:** `[[Note Name#^block-id]]` — Links to a specific block in the note
- **Absolute path:** `[[folder/Note Name]]` — Links to a note in a subfolder
- **Relative path:** `[[../Note Name]]` — Links to a note in a parent folder

### Example

```
Check out the [[Meeting Notes]] for details.

See the [[Project Overview|project overview]] for more context.

Refer to [[Tasks#Active Tasks]] for current work.
```

### Best Practices

- Use the display text parameter `[[Note Name|Display Text]]` to make links more readable
- Avoid spaces in note names — use dashes or underscores instead: `[[project-overview]]`
- Use consistent naming conventions throughout your vault (e.g., kebab-case, CamelCase)
- For linking to headings, prefer using the heading text exactly as it appears in the target note

## Embeds

Embed content from other notes directly into your current note. Embeds are similar to wikilinks but start with `!`.

### Quick Reference

```
![[Note Name]]
![[Note Name#Heading]]
![[Image.png]]
```

### Embed Syntax

- **Basic embed:** `![[Note Name]]` — Embeds the entire note
- **Embed heading:** `![[Note Name#Heading]]` — Embeds content from a specific heading
- **Embed block:** `![[Note Name#^block-id]]` — Embeds a specific block
- **Embed image:** `![[Image.png]]` — Embeds an image from your vault
- **Embed with alt text:** `![[Note Name|alt text]]` — Displays alternative text for the embed

### Example

```
Here's a summary of the meeting:

![[Meeting Notes#Agenda]]

![Diagram of the system architecture](../../images/architecture.png)
```

### Best Practices

- Use embeds to keep your notes modular and reduce duplication
- Embed headings or blocks rather than entire notes when you only need specific content
- Use the `alt text` parameter to provide context for embeds
- Remember that embeds update dynamically — if the source note changes, the embed reflects those changes
- Path handling for embeds works the same as for wikilinks

## Callouts

Callouts are styled blocks for highlighting important information. They start with `>` followed by `![type]`.

### Quick Reference

```
> [!note] Title
> Content here
```

### Callout Types

Obsidian supports these callout types:

| Type | Aliases | Description |
| ---- | ------- | ----------- |
| `note` | `notes`, `seealso` | General information |
| `abstract` | `summary`, `tldr` | Summary or TL;DR |
| `info` | `todo` | Informational |
| `tip` | `hint`, `important` | Helpful suggestions |
| `warning` | `caution`, `attention` | Warnings |
| `danger` | `error`, `bug` | Errors or dangerous actions |
| `example` | `sample` | Examples |
| `quote` | `cite` | Quotations |

### Callout Syntax

```
> [!note]
> This is a callout with just a type

> [!tip] Custom Title
> This callout has a custom title

> [!warning] Important
> Be careful when doing this
```

### Foldable Callouts

Add `+` or `-` after the type to control foldability:

- `> [!note]+` — Expanded by default (can be collapsed)
- `> [!note]-` — Collapsed by default (can be expanded)

### Nested Callouts

You can nest callouts by adding more `>` characters:

```
> [!note]
> Outer callout
> > [!tip]
> > Nested callout
```

### Best Practices

- Use callouts consistently to organize information in your vault
- Choose appropriate callout types for the content (e.g., `warning` for important cautions)
- Use custom titles to provide additional context
- Consider using foldable callouts for long content that readers may want to collapse
- Avoid overusing callouts — they lose their impact if everything is highlighted

## Standard Markdown

Obsidian supports standard markdown with some enhancements.

### Text Formatting

| Markdown | Result |
| -------- | ------ |
| `**bold**` | **bold** |
| `*italic*` | *italic* |
| `~~strikethrough~~` | ~~strikethrough~~ |
| `` `inline code` `` | `inline code` |
| `==highlight==` | ==highlight== |

### Lists

```
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Second item
   - Nested ordered item

- [ ] Unchecked task
- [x] Checked task (note the lowercase x)
```

### Headings

```
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

### Tables

```
| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

### Code Blocks

````
```javascript
function hello() {
  console.log("Hello, World!");
}
```
````

### Horizontal Rules

Use three or more dashes, asterisks, or underscores on a line:

```
---
```

or

```
***
```

## Obsidian-Only Syntax

### Highlights

```
==highlighted text==
```

### Footnotes

```
Here is a footnote[^1] reference.

[^1]: Here is the footnote definition.
```

### Math

```
$$
\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

Inline math: `$E = mc^2$`

### Comments

```
%% This is a comment that won't appear in reading view %%
```

### Attribute Blocks

Add attributes to elements:

```
This is a paragraph {#my-anchor .my-class}
```

## File Naming

- Use lowercase letters, numbers, and dashes
- Avoid special characters and spaces
- Example: `2024-01-project-meeting-notes.md`
- Use dates at the beginning for chronological notes: `2024-01-15-meeting-notes.md`
- Use consistent naming conventions throughout your vault
