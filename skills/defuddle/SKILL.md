---
name: defuddle
description: Extract clean markdown from web pages using Defuddle, removing clutter to save tokens. Use this skill whenever the user wants to extract clean content from web pages, clean up copied content, or remove unwanted formatting from text.
---

# Defuddle Skill

Defuddle is a tool for extracting clean markdown from web pages, removing clutter like navigation, ads, footers, and other non-content elements. It helps save tokens by extracting only the relevant content.

## When to Use Defuddle

Use Defuddle when you need to:

- Extract clean content from web pages
- Remove navigation, ads, and other non-content elements
- Convert web content to clean markdown
- Clean up copied text that has unwanted formatting
- Prepare web content for AI processing (to save tokens)

## How Defuddle Works

Defuddle analyzes web pages and identifies:

- **Main content** — The primary article, post, or information
- **Navigation** — Menus, breadcrumbs, sidebars
- **Ads and trackers** — Advertising, analytics scripts
- **Footers** — Copyright, links, contact info
- **Comments** — User comments (optional)

It then extracts only the clean content in markdown format.

## Using Defuddle

### Basic Usage

```bash
defuddle https://example.com/article
```

### Options

| Option | Description |
| ------ | ----------- |
| `--url` | URL to extract from |
| `--output` | Output file (default: stdout) |
| `--include-comments` | Include user comments |
| `--include-images` | Include image references |
| `--verbose` | Show detailed output |

### Example Commands

```bash
# Extract from URL
defuddle https://example.com/page

# Save to file
defuddle https://example.com/page --output clean.md

# Include comments
defuddle https://example.com/page --include-comments

# Verbose output
defuddle https://example.com/page --verbose
```

## Integration with Other Skills

Defuddle works well with other skills:

1. **obsidian-markdown** — After extracting with Defuddle, use obsidian-markdown to format for Obsidian
2. **recording-ideas** — Save extracted content as notes in your vault

### Workflow Example

```
1. Use defuddle to extract content from web page
2. Review and edit the extracted markdown
3. Use obsidian-markdown skill to add Obsidian-specific formatting
4. Save to your vault using appropriate naming and properties
```

## Best Practices

1. **Review extracted content** — Always review and edit the output
2. **Add source attribution** — Include the original URL as a reference
3. **Clean up formatting** — Some formatting may need manual adjustment
4. **Extract strategically** — Focus on the main content you need
5. **Save tokens** — Use defuddle before processing large amounts of web content with AI

## Alternative: Manual Extraction

If Defuddle is not available, you can manually extract clean content:

1. Copy the main content from the web page
2. Paste into a markdown editor
3. Remove unwanted formatting
4. Add appropriate markdown syntax

### Quick Manual Tips

- Use `Ctrl+Shift+V` in most apps to paste as plain text
- Use find/replace to remove repeated elements
- Add headers with `#`, `##`, etc.
- Use lists for bullet points
- Use code blocks for any code snippets
