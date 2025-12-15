import os
import json
from bs4 import BeautifulSoup
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_JSON = os.path.join(BASE_DIR, 'Data', 'missing_articles.json')

def extract_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        # Try to find title
        title = "Sem Título"
        
        # Priority 1: Title tag
        if soup.title:
            title = soup.title.string
            
        # Priority 2: h1 or h2
        if title == "Sem Título" or not title:
             h1 = soup.find('h1')
             if h1: title = h1.get_text().strip()
             
        # Extract content
        # Usually in blockquote for these files based on previous scripts
        content_tag = soup.find('blockquote')
        if not content_tag:
            content_tag = soup.body
            
        if content_tag:
            # We want the inner HTML or text. Let's keep HTML for structure key
            # But the user might want text for translation. 
            # Let's keep a simplified HTML string.
            content = str(content_tag)
        else:
            content = ""
            
        return {
            "source_file": os.path.relpath(file_path, BASE_DIR),
            "title": title.strip() if title else "No Title",
            "content_original": content
        }
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    # Target specific files identified in the report
    # We could parse the report, but let's just scan for them using the same logic to be robust
    
    target_dirs = ['search1/kouwa', 'sasshi', 'search2/kikou', 'gosanka']
    target_files_specific = [
        'search1/kouwa/s290323.html',
        'search1/kouwa/s290401.html',
        'search1/kouwa/s280706.html',
        'sasshi/kesshin.html',
        'search2/kikou/eiga.html'
    ]
    
    # Also scan gosanka
    
    missing_items = []
    
    # 1. Add specific files if they exist
    for rel_path in target_files_specific:
        full_path = os.path.join(BASE_DIR, rel_path)
        if os.path.exists(full_path):
            data = extract_content(full_path)
            if data:
                missing_items.append(data)
                
    # 2. Scanning directories for others (like gosanka) that are NOT in the manifest
    # This requires loading the manifest again to exclude existing one?
    # Or just rely on the user's "yes" to the list I gave.
    # The list I gave had "gosanka/ (~66 files)".
    
    # Let's grab all from gosanka
    gosanka_dir = os.path.join(BASE_DIR, 'gosanka')
    if os.path.exists(gosanka_dir):
        for root, dirs, files in os.walk(gosanka_dir):
            for file in files:
                if file.endswith(".html"):
                    full_path = os.path.join(root, file)
                    # We should check if it's already translated, but for now let's just add it
                    # The user asked for "missing" ones.
                    # To be safe, let's assume if it's in gosanka dir it's what they want
                    data = extract_content(full_path)
                    if data:
                         missing_items.append(data)

    print(f"Extracted {len(missing_items)} items.")
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(missing_items, f, indent=2, ensure_ascii=False)
        
    print(f"Saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
