import sys
import os
import re
import urllib.request
import urllib.parse
import json
from bs4 import BeautifulSoup

# --- Configuration ---
# Set your Obsidian vault root directory
OBSIDIAN_VAULT_DIR = r"C:\Users\Aryan\OneDrive\Documents\Obsidian Vault\Books" # Update this to your real vault path

# Set the attachment folder path relative to the vault root
ATTACHMENT_DIR_REL = r"C:\Users\Aryan\OneDrive\Documents\Obsidian Vault\00_Helper\Attachments"
# ---------------------

def get_book_cover(book_title, author, save_path):
    """Fetches the book cover from Open Library API and saves it."""
    print(f"Searching for cover image for '{book_title}'...")
    
    # Construct the search query for Open Library
    query = f"title={urllib.parse.quote(book_title)}"
    if author:
        # Get just the last name for better matching in Open Library
        author_last = author.split(',')[0].strip() if ',' in author else author
        query += f"&author={urllib.parse.quote(author_last)}"
        
    search_url = f"https://openlibrary.org/search.json?{query}&limit=5"
    
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            if 'docs' in data and len(data['docs']) > 0:
                # Find the first item with an isbn or cover_i
                for doc in data['docs']:
                    if 'cover_i' in doc:
                        cover_id = doc['cover_i']
                        image_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                        break
                    elif 'isbn' in doc and len(doc['isbn']) > 0:
                        isbn = doc['isbn'][0]
                        image_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                        break
                else:
                    print(f"No cover image found in the Open Library results for '{book_title}'.")
                    return False
                    
                # Download the image
                req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as img_resp, open(save_path, 'wb') as out_file:
                    out_file.write(img_resp.read())
                print(f"Successfully downloaded cover image to {save_path}")
                return True
                        
            else:
                print(f"No book found in Open Library API for '{book_title}'.")
                
    except Exception as e:
        print(f"Error fetching book cover: {e}")
        
    return False

def get_book_description(book_title, author):
    """Fetches the book summary/description from Open Library API."""
    print(f"Searching for book description for '{book_title}'...")
    
    query = f"title={urllib.parse.quote(book_title)}"
    if author:
        author_last = author.split(',')[0].strip() if ',' in author else author
        query += f"&author={urllib.parse.quote(author_last)}"
        
    search_url = f"https://openlibrary.org/search.json?{query}&limit=3"
    
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            if 'docs' in data and len(data['docs']) > 0:
                # Find the first item with a valid work key
                for doc in data['docs']:
                    if 'key' in doc:
                        work_key = doc['key']
                        
                        # Go to the work page to get the description
                        work_url = f"https://openlibrary.org{work_key}.json"
                        work_req = urllib.request.Request(work_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(work_req) as work_response:
                            work_data = json.loads(work_response.read().decode())
                            
                            description = work_data.get('description')
                            if description:
                                # the description is sometimes a dict with 'value' key
                                if isinstance(description, dict) and 'value' in description:
                                    return description['value']
                                elif isinstance(description, str):
                                    return description
                        # If the key had no description, try the next search result
                
                print(f"No description found in the Open Library results for '{book_title}'.")
            else:
                print(f"No book found in Open Library API for '{book_title}'.")
                
    except Exception as e:
        print(f"Error fetching book description: {e}")
        
    return None

def convert_kindle_html_to_obsidian(html_path, vault_dir, attachment_rel_dir):
    """Parses the Kindle HTML and creates the Markdown file and downloads the cover."""
    print(f"Parsing HTML file: {html_path}")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return

    # Extract Book Title and Author
    book_title_elem = soup.find(class_='bookTitle')
    author_elem = soup.find(class_='authors')
    
    if not book_title_elem:
        print("Could not find book title in HTML. Exiting.")
        return
        
    book_title = book_title_elem.get_text(strip=True)
    author = author_elem.get_text(strip=True) if author_elem else ""
    
    print(f"Found book: '{book_title}' by {author}")
    
    # Prepare filenames and paths
    safe_title = re.sub(r'[\\/*?:"<>|]', "", book_title) # Remove invalid characters for filenames
    image_filename = safe_title.replace(" ", "_") + ".jpg"
    md_filename = f"{safe_title}.md"
    
    # Ensure attachment directory exists
    attachment_abs_dir = os.path.join(vault_dir, attachment_rel_dir)
    os.makedirs(attachment_abs_dir, exist_ok=True)
    
    image_save_path = os.path.join(attachment_abs_dir, image_filename)
    md_save_path = os.path.join(vault_dir, md_filename)
    
    # 1. Fetch Book Cover
    cover_downloaded = get_book_cover(book_title, author, image_save_path)
    
    # 1.5 Fetch Book Description
    description_text = get_book_description(book_title, author)
    
    # 2. Extract Highlights
    highlights = []
    # Kindle exports usually have noteHeading (the metadata) and noteText (the highlight)
    for note_div in soup.find_all(class_='noteText'):
        # Check the preceding sibling for metadata like "Highlight" to skip bookmarks/notes if needed.
        # The user requested to remove lines containing "Highlight", but the HTML structure has them separate headers.
        # We will just extract the `noteText` directly.
        text = note_div.get_text(strip=True)
        if text:
            highlights.append(text)
            
    # 3. Generate Markdown Content
    print(f"Generating Markdown file with {len(highlights)} highlights...")
    md_lines = []
    
    # Add YAML Frontmatter
    md_lines.append("---")
    if author:
        md_lines.append(f"author: {author}")
    if cover_downloaded:
        md_lines.append(f"cover: {image_filename}")
    md_lines.append("---")
    
    # Add Cover Image link if downloaded
    if cover_downloaded:
        # Resize image for obsidian just like the user's template `![[image.png| 200]]`
        # Unfortunately Obsidian standard md vs wikilinks behaves differently.
        # Following user template, they use wikilink syntax: `![[the-rosie-project.png| 200]]`
        md_lines.append(f"![[{image_filename}| 200]]")
        
    if description_text:
        # Clean up description (remove extra newlines and trim)
        clean_desc = " ".join(description_text.split())
        md_lines.append(f"**About Book:** {clean_desc}")
        md_lines.append("")
        
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("# Highlights")
    for highlight in highlights:
        # Clean up any potential internal newlines in the highlight text
        clean_highlight = " ".join(highlight.split())
        md_lines.append(f"- {clean_highlight}")
        
    # 4. Save Markdown File
    try:
        with open(md_save_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_lines) + "\n")
        print(f"Successfully created Markdown file at: {md_save_path}")
    except Exception as e:
        print(f"Error saving Markdown file: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # A file was passed as an argument (e.g., via drag and drop)
        input_file = sys.argv[1]
        convert_kindle_html_to_obsidian(input_file, OBSIDIAN_VAULT_DIR, ATTACHMENT_DIR_REL)
    else:
        print("Usage: Please drag and drop a Kindle HTML file onto this script.")
        print("Or run from command line: python kindle_to_obsidian.py <path_to_html_file>")
        print()
    
    # Pause so the console window doesn't close immediately if you drag & drop on Windows
    input("Press Enter to exit...")
