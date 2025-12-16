
import re
import os
from bs4 import BeautifulSoup

HTML_FILE = 'gosanka/yamato.html'
MARKDOWN_FILE = 'Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'

def parse_html_poems(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    poems = []
    current_category = None
    
    # Iterate through table rows in the main content area
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if not cols: continue
            
            # Check for Category Title
            text_content = row.get_text(strip=True)
            bold = row.find('strong')
            
            # If a row has a strong tag and NO poem number in the first column, it's likely a header
            first_col_text = cols[0].get_text(strip=True)
            
            # Categories are often "春すぎぬ" or "日　　月"
            # They are usually in the second column if the first is empty or just spacing
            if not first_col_text.isdigit() and bold:
                 cat_title = bold.get_text(strip=True).replace('　', ' ')
                 # Filter out date lines or other non-titles if necessary
                 if cat_title and "昭和" not in cat_title:
                     current_category = cat_title
            
            # Check for Poem
            poem_num = cols[0].get_text(strip=True)
            if poem_num.isdigit():
                content_col = cols[1]
                fonts = content_col.find_all('font')
                original_text = ""
                reading_text = ""
                
                for ft in fonts:
                    fs = ft.get('size')
                    ft_text = ft.get_text(strip=True)
                    if fs == '3':
                        original_text = ft_text
                    elif fs == '1':
                        reading_text = ft_text
                
                if not original_text and len(fonts) > 0:
                    original_text = fonts[-1].get_text(strip=True)
                
                poems.append({
                    'id': int(poem_num),
                    'category': current_category,
                    'original': original_text,
                    'reading': reading_text
                })

    return poems

def parse_markdown_poems(path):
    if not os.path.exists(path):
        return set()
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ids = set()
    matches = re.finditer(r'##\s+(\d+)', content)
    for m in matches:
        ids.add(int(m.group(1)))
    return ids

def main():
    print("Parsing HTML...")
    html_items = parse_html_poems(HTML_FILE)
    print(f"Found {len(html_items)} poems in HTML.")
    
    print("Parsing Markdown...")
    md_ids = parse_markdown_poems(MARKDOWN_FILE)
    print(f"Found {len(md_ids)} poems in Markdown.")
    
    html_ids = set(p['id'] for p in html_items)
    missing = html_ids - md_ids
    
    print(f"Missing IDs count: {len(missing)}")
    if missing:
        sorted_missing = sorted(list(missing))
        print(f"Missing IDs (first 50): {sorted_missing[:50]}")
        print(f"Missing IDs (last 50): {sorted_missing[-50:]}")
    
    # Save missing to file for inspection
    with open('Data/missing_poems_yamato.txt', 'w', encoding='utf-8') as f:
        for p in html_items:
            if p['id'] in missing:
                f.write(f"{p['id']}\t{p['category']}\t{p['original']}\n")

if __name__ == "__main__":
    main()
