# Kindle Highlights to Obsidian Automator

This repository provides an automated Python pipeline designed to seamlessly integrate Amazon Kindle reading highlights into an Obsidian personal knowledge management vault.

## Overview

Exporting highlights from a Kindle device via HTML yields a file that contains formatting and structural artifacts unnecessary for a clean markdown note. This script parses the provided Kindle HTML export file, extracting only the relevant metadata (title, author) and the highlighted text. 

Furthermore, the script interfaces with the Open Library API to automatically retrieve the book's cover image and description. The collected data is then formatted into Obsidian-flavored Markdown, complete with YAML frontmatter, wikilink image formatting, and a structured bulleted list of highlights.

## Features

- **Automated Parsing**: Utilizes BeautifulSoup to cleanly extract highlight text while excluding unnecessary chapter headings and Kindle HTML metadata.
- **API Integration**: Connects to the Open Library API to fetch and download the correct book cover image and book summary description based on the title and author.
- **Obsidian Formatting**: Generates a `.md` file formatted specifically for Obsidian, including:
  - YAML frontmatter (`author`, `cover`)
  - Image wikilinks with resize parameters
  - Clean markdown separation of book details and reading highlights.
- **Frictionless Execution**: Supports drag-and-drop file execution on Windows via command-line argument parsing.

## Requirements

- Python 3.6+
- `beautifulsoup4`

Install the required dependencies via:
```bash
pip install -r requirements.txt
```

## Setup & Configuration

Before running the script, you must configure the destination paths for your Obsidian Vault. 

Open `kindle_to_obsidian.py` in your preferred text editor and update the constants at the top of the file:

```python
# --- Configuration ---
# Set your Obsidian vault root directory
OBSIDIAN_VAULT_DIR = r"C:\Path\To\Your\Obsidian Vault\Books"

# Set the attachment folder path relative to the vault root
ATTACHMENT_DIR_REL = r"C:\Path\To\Your\Obsidian Vault\00_Helper\Attachments"
# ---------------------
```

## Usage

### Method 1: Drag and Drop (Windows)
The most efficient way to use the script is to simply drag and drop your exported Kindle HTML file (`Notebook.html`) directly onto the `kindle_to_obsidian.py` executable file. The script will automatically parse the file and deposit the generated `.md` note and image into your configured Obsidian directories.

### Method 2: Command Line
You can also execute the script directly from the terminal, passing the HTML file as an argument:
```bash
python kindle_to_obsidian.py "path/to/your/Notebook.html"
```
