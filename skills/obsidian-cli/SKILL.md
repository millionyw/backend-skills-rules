---
name: obsidian-cli
description: Interact with Obsidian vaults via the Obsidian CLI including plugin and theme development. Use this skill whenever the user wants to interact with Obsidian using the command line, develop plugins, work with the Obsidian API, or manage Obsidian vaults programmatically.
---

# Obsidian CLI Skill

This skill enables you to work with Obsidian vaults and develop plugins using the Obsidian CLI and API.

## Obsidian CLI

The Obsidian CLI (command-line interface) allows you to interact with Obsidian from the terminal. It enables tasks like:

- Creating new vaults
- Running Obsidian in dev mode
- Building plugins
- Managing vault settings

### Installation

```bash
npm install -g obsidian
```

### Basic Commands

```bash
# Create a new vault
obsidian new "Vault Name"

# Open a vault
obsidian open "Vault Path"

# Run Obsidian in dev mode for plugin development
obsidian dev "Vault Path"

# Build a plugin
obsidian build-plugin

# Publish a plugin
obsidian publish
```

## Plugin Development

Obsidian plugins extend Obsidian's functionality. They consist of:

- `manifest.json` — Plugin metadata
- `main.js` — Plugin code
- `styles.css` — Optional styles
- `data.json` — Optional persistent data

### manifest.json

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "A description of my plugin",
  "author": "Your Name",
  "authorUrl": "https://yourwebsite.com",
  "isDesktopOnly": false
}
```

### Basic Plugin Structure

```javascript
import { Plugin } from 'obsidian';

export default class MyPlugin extends Plugin {
  async onload() {
    console.log('Loading my plugin');
    
    // Add a command
    this.addCommand({
      id: 'my-command',
      name: 'My Command',
      callback: () => {
        console.log('Command executed');
      }
    });
    
    // Add a status bar item
    this.addStatusBarItem().setText('My Plugin Loaded');
  }

  onunload() {
    console.log('Unloading my plugin');
  }
}
```

### Plugin API Overview

#### Adding Commands

```javascript
this.addCommand({
  id: 'command-id',
  name: 'Command Name',
  hotkeys: [{ modifiers: ['Mod', 'Shift'], key: 'k' }],
  callback: () => {
    // Command logic
  }
});
```

#### Registering Events

```javascript
// Register an event
this.registerEvent(
  this.app.workspace.on('editor-change', (editor, info) => {
    // Handle editor changes
  })
);

// Or use a simpler approach
this.app.workspace.on('editor-change', this.handleChange.bind(this));
```

#### Creating Modals

```javascript
import { Modal } from 'obsidian';

class MyModal extends Modal {
  constructor(app) {
    super(app);
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.setText('Hello from my modal!');
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}

// Show the modal
new MyModal(this.app).open();
```

#### Adding Settings Tab

```javascript
import { Setting } from 'obsidian';

export default class MyPlugin extends Plugin {
  async onload() {
    this.addSettingTab(new MySettingTab(this.app, this));
  }
}

class MySettingTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();
    
    new Setting(containerEl)
      .setName('My Setting')
      .setDesc('Description of my setting')
      .addText(text => text
        .setValue(this.plugin.settings.mySetting)
        .onChange(async (value) => {
          this.plugin.settings.mySetting = value;
          await this.plugin.saveSettings();
        }));
  }
}
```

## Vault Management

### Opening and Reading Files

```javascript
import { TFile } from 'obsidian';

// Read a file
async function readFile(app, path) {
  const file = app.vault.getAbstractFileByPath(path);
  if (file instanceof TFile) {
    return await app.vault.read(file);
  }
  return null;
}

// Get all files
function getAllFiles(app) {
  return app.vault.getFiles();
}

// Get files in a folder
function getFilesInFolder(app, folderPath) {
  const folder = app.vault.getAbstractFileByPath(folderPath);
  if (folder) {
    return folder.children.filter(f => f instanceof TFile);
  }
  return [];
}
```

### Creating and Writing Files

```javascript
// Create a new note
async function createNote(app, path, content) {
  await app.vault.create(path, content);
}

// Create a note from template
async function createFromTemplate(app, templatePath, newPath, variables) {
  const template = await readFile(app, templatePath);
  let content = template;
  
  // Replace variables
  for (const [key, value] of Object.entries(variables)) {
    content = content.replace(new RegExp(`{{${key}}}`, 'g'), value);
  }
  
  await app.vault.create(newPath, content);
}
```

### File Metadata

```javascript
// Get file metadata
function getFileMetadata(app, path) {
  const file = app.vault.getAbstractFileByPath(path);
  if (file instanceof TFile) {
    return app.metadataCache.getFileCache(file);
  }
  return null;
}

// Get frontmatter/properties
function getFrontmatter(app, path) {
  const file = app.vault.getAbstractFileByPath(path);
  if (file instanceof TFile) {
    const cache = app.metadataCache.getFileCache(file);
    return cache?.frontmatter;
  }
  return null;
}
```

## Working with Editor

### Editor Commands

```javascript
// Insert text at cursor
function insertText(editor) {
  const cursor = editor.getCursor();
  editor.replaceRange('Hello, World!', cursor);
}

// Get selected text
function getSelection(editor) {
  return editor.getSelection();
}

// Replace selection
function replaceSelection(editor, text) {
  const selection = editor.getSelection();
  editor.replaceSelection(text);
}

// Get current line
function getCurrentLine(editor) {
  const cursor = editor.getCursor();
  return editor.getLine(cursor.line);
}
```

### Inserting Blocks

```javascript
// Insert a callout
function insertCallout(editor, type, title, content) {
  const text = `> [!${type}] ${title}\n> ${content}`;
  editor.replaceSelection(text);
}

// Insert a code block
function insertCodeBlock(editor, language, code) {
  const text = `\`\`\`${language}\n${code}\n\`\`\``;
  editor.replaceSelection(text);
}
```

## Best Practices

1. **Use TypeScript** — TypeScript provides better autocomplete and type checking
2. **Follow Obsidian's API** — Use official APIs and avoid private methods
3. **Test in dev mode** — Always test plugins in Obsidian's dev mode
4. **Handle errors gracefully** — Add try-catch blocks and user-friendly error messages
5. **Save settings properly** — Always call `saveSettings()` after changing settings
6. **Clean up in onunload** — Remove event listeners and clean up resources
7. **Use the manifest correctly** — Ensure all required fields are present
8. **Version your plugin** — Use semantic versioning for releases
