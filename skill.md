---
name: kindle-obsidian
description: Convert Kindle HTML notes to Obsidian notes using custom script
version: 1.0

triggers:
  - type: whatsapp_file

entrypoint: handler.py
---

# Kindle → Obsidian Automation Skill

## Purpose

This skill converts Kindle HTML notes into formatted Obsidian markdown notes.

It is primarily used when the user sends an exported Kindle highlights file.

## When to Use

Use this skill when:

* The user sends an HTML file containing notes or highlights (with or without .html extension)
* The user asks to process Kindle highlights
* A WhatsApp message contains an HTML file attachment

## Workflow

When triggered:

1. Receive the HTML file from WhatsApp.
2. Pass the file to `handler.py`.
3. Run the Kindle-to-Obsidian conversion script.
4. Generate Markdown notes formatted for Obsidian.
5. Save the output in the configured Obsidian vault.

## Expected Input

* HTML file exported from Kindle highlights.

## Output

* Markdown notes stored in the Obsidian vault.
* Confirmation message that processing completed.

## Notes

Ignore files that are not HTML.
If processing fails, return the error message.
