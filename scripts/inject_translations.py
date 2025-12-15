
import json
import os
import markdown
from bs4 import BeautifulSoup
import re

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(BASE_DIR, 'Data', 'teachings_manifest.json')
DATA_DIR = os.path.join(BASE_DIR, 'Data')

def load_all_translations(manifest_path):
    print(f"Loading manifest from {manifest_path}...")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    all_translations = []
    for filename in manifest.get('files', []):
        part_path = os.path.join(DATA_DIR, filename)
        print(f"Loading {part_path}...")
        try:
            with open(part_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_translations.extend(data)
                else:
                    print(f"Warning: {filename} does not contain a list.")
        except FileNotFoundError:
            print(f"Error: File {part_path} not found.")
            
    return all_translations

def find_file(filename, search_path):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def md_to_html(md_text):
    if not md_text:
        return ""
    # Simple markdown conversion
    html = markdown.markdown(md_text)
    # Adjust font sizes or styles if necessary to match original look roughly
    # The original had <font size="4"> for title and size 3 for body in some places
    # We will wrap the whole thing in a div or just let it be standard HTML
    return html

def inject_translation(html_path, pt_content, title):
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Target the blockquote which seems to contain the main text in these files
    target_tag = soup.find('blockquote')
    
    if not target_tag:
        print(f"Warning: No <blockquote> found in {html_path}. Skipping.")
        return False

    # Create new content
    # Converting markdown to HTML
    html_content = md_to_html(pt_content)
    
    # We want to preserve the styling if possible, but the user said "just connect data"
    # and "don't change layout". 
    # The original inside blockquote has <p><font...>Title</font>... text ... </p>
    # We will replace the inner HTML of blockquote with our new HTML.
    # To keep similar styling, we might want to wrap our content or rely on CSS.
    # The existing CSS is seiji.html links to ../../style4.css
    
    # Let's create a new structure for the translated content
    # We'll put the title in h2 and content in p, trusting the browser defaults or style4.css
    
    new_div = soup.new_tag('div')
    new_div['class'] = 'translated-content'
    
    # Parse the generated HTML from markdown to insert it as tags, not string
    content_soup = BeautifulSoup(html_content, 'html.parser')
    new_div.append(content_soup)

    # Clear existing content and append new
    target_tag.clear()
    target_tag.append(new_div)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    return True

def main():
    translations = load_all_translations(MANIFEST_PATH)
    
    count = 0
    success_count = 0
    
    print(f"Found {len(translations)} items. Starting injection...")

    for item in translations:
        source_file = item.get('source_file')
        content_ptbr = item.get('content_ptbr')
        title = item.get('title')

        if not source_file or not content_ptbr:
            continue

        # Find the actual file path
        full_path = find_file(source_file, BASE_DIR)
        
        if full_path:
            # print(f"Processing {source_file} at {full_path}...")
            if inject_translation(full_path, content_ptbr, title):
                success_count += 1
            else:
                print(f"Failed to inject into {source_file}")
        else:
            print(f"Could not find file: {source_file}")
            
        count += 1
        if count % 100 == 0:
            print(f"Processed {count} items...")

    print(f"Finished. Successfully injected {success_count} out of {len(translations)} items.")

if __name__ == "__main__":
    main()
