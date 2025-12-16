
import json
import os
import re
from bs4 import BeautifulSoup

MD_FILE = 'Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'
HTML_FILE = 'gosanka/yamato.html'

def load_translations():
    print("Loading MD translations...")
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse Poems
    # Pattern: ## [ID]. [Title]
    # Followed by **Tradução Artística:** "Text"
    
    poems = {}
    
    # Split by ## [Number]
    parts = re.split(r'(^|\n)##\s+(\d+)\.?', content)
    
    for i in range(2, len(parts), 3):
        pid = int(parts[i])
        block = parts[i+1]
        
        # Extract Title
        # The block usually starts with " Title\n"
        title_match = re.match(r'\s*(.+?)\n', block)
        title = title_match.group(1).strip() if title_match else ""
        
        # Extract Translation Text
        # Pattern: **Tradução Artística:**\s*\n\s*"(.+?)"
        # Note: formatting might vary (newlines inside quotes)
        trans_match = re.search(r'\*\*Tradução Artística:\*\*\s*\n\s*"?(.+?)"?\s*\n', block, re.DOTALL)
        trans_text = ""
        if trans_match:
            trans_text = trans_match.group(1).strip().replace('\n', ' ')
            # Remove quotes if captured
            if trans_text.startswith('"') and trans_text.endswith('"'):
                trans_text = trans_text[1:-1]
        
        poems[pid] = {
            'title': title,
            'text': trans_text
        }
        
    # Check for Category translations?
    # We replaced them in MD file: # 📂 SEÇÃO: [Portuguese] ([Original])
    # We need to map [Original] -> [Portuguese]
    
    categories = {}
    cat_matches = re.findall(r'# 📂 SEÇÃO: (.+?) \((.+?)\)', content)
    for pt, jp in cat_matches:
        # Map Japanese Key (trimmed) to Portuguese Title
        categories[jp.strip()] = pt.strip()
        
    return poems, categories

def rebuild_html():
    poems, categories = load_translations()
    print(f"Loaded {len(poems)} poems and {len(categories)} categories.")
    
    with open(HTML_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Strategy:
    # 1. Update Category Rows
    # 2. Update Poem Rows (replace JP with PT)
    # The JP content is already preserved in #jp-content at the bottom (or needs to be regenerated if missing)
    # Actually, the file `yamato.html` has Japanese in the table. 
    # We will OVERWRITE the table with Portuguese.
    # AND Ensure #jp-content contains the ORIGINAL table or text.
    
    # Wait, `inject_bilingual_static.py` creates `#jp-content` from the *current* content before modifying?
    # No, usually it expects #jp-content to exist or creates it.
    
    # If we overwrite the main table, we lose the visible Japanese.
    # We must ensure the Japanese is safe.
    # Check if #jp-content exists.
    jp_div = soup.find(id='jp-content')
    if not jp_div:
        print("Creating #jp-content backup...")
        # Create a copy of the main content wrapper?
        # The structure is complex (<table>). 
        # A simple approach: 
        # Clone the main table?
        # Or just assume the injection script will handle the view switching if we have both.
        # But we need to POPULATE the main view with PT.
        
        # Let's clone the body content into jp-content if it's not there?
        main_div = soup.find('div', align='center') # The main wrapper usually
        if main_div:
             import copy
             jp_copy = copy.copy(main_div)
             new_div = soup.new_tag('div', id='jp-content', style='display:none;')
             new_div.append(jp_copy)
             soup.body.append(new_div)
    
    # Prepare to update THE FIRST table/div (which is the PT view) 
    # Iterate tables again
    tables = soup.find_all('table')
    
    updates_count = 0
    
    for table in tables:
        # Skip if inside jp-content
        if table.find_parent(id='jp-content'):
            continue
            
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if not cols: continue
            
            # Category Update
            bold = row.find('strong')
            first_col_text = cols[0].get_text(strip=True)
            if not first_col_text.isdigit() and bold:
                 cat_jp = bold.get_text(strip=True).replace('　', ' ').strip()
                 # Try to find translation
                 # The regex might missed spaces.
                 # Heuristic matching
                 if cat_jp in categories:
                     bold.string = categories[cat_jp] 
                 else:
                     # Try partial match or exact match keys from extracted list
                     # Sometimes the html has extra spaces
                     pass

            # Poem Update
            poem_num_text = cols[0].get_text(strip=True)
            if poem_num_text.isdigit():
                pid = int(poem_num_text)
                if pid in poems:
                    # Update Content Column (Index 1)
                    content_col = cols[1]
                    
                    data = poems[pid]
                    pt_title = data['title']
                    pt_text = data['text']
                    
                    # Create new HTML content
                    # Format: <b>Title</b><br>Text
                    
                    # Clear existing content
                    content_col.clear()
                    
                    # Add Title
                    title_tag = soup.new_tag('b')
                    title_tag.string = pt_title
                    title_font = soup.new_tag('font', size='2', color='#000080') # Navy for PT title
                    title_font.append(title_tag)
                    content_col.append(title_font)
                    
                    content_col.append(soup.new_tag('br'))
                    
                    # Add Text
                    text_font = soup.new_tag('font', size='3') # Standard size
                    text_font.string = pt_text
                    content_col.append(text_font)
                    
                    updates_count += 1

    print(f"Updated {updates_count} poems to Portuguese in HTML.")
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == "__main__":
    rebuild_html()
