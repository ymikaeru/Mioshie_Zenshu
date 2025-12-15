import json
import os
import re
from pathlib import Path

# Config
INDEX_FILE = 'Data/advanced_search_index.json'
DATA_DIR = 'Data'
PROJECT_ROOT = '.' # Assuming running from project root

def load_data():
    print("Loading index...")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    return index

def load_translations():
    translations = {} # part_file -> list of items
    print("Loading translations...")
    for f in os.listdir(DATA_DIR):
        if f.startswith('teachings_translated_part') and f.endswith('.json'):
            path = os.path.join(DATA_DIR, f)
            print(f"  Loading {f}...")
            with open(path, 'r', encoding='utf-8') as fp:
                translations[f] = json.load(fp)
    return translations

def get_japanese_content(index_item, translations):
    part_file = index_item.get('part_file')
    if not part_file or part_file not in translations:
        return None
    
    item_id = index_item.get('id')
    for t_item in translations[part_file]:
        if t_item['id'] == item_id:
            return t_item.get('content')
    return None

def format_japanese_text(text):
    if not text: return ""
    # Simple splitting for readability
    if '\n' in text:
        return text.replace('\n', '<br>')
    else:
        return text.replace('。', '。<br><br>')

def inject_toggle(html_path, jp_content):
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  [MISSING] {html_path}")
        return False

    # Check for marker
    if '<!-- LANGUAGE TOGGLE INJECTED -->' in content:
        # Already injected, we might want to update the JP content though?
        # For now, let's skip to avoid duplicating or messing up regex
        # Or better: remove old block and re-inject
        content = re.sub(r'<!-- LANGUAGE TOGGLE INJECTED start -->.*?<!-- LANGUAGE TOGGLE INJECTED end -->', '', content, flags=re.DOTALL)
        # print("  [UPDATE] Re-injecting...")
    
    # Target insertion point: Before <div class="translated-content">
    # If not found, try <blockquote>
    
    target_pattern = r'(<div class="translated-content">)'
    if not re.search(target_pattern, content):
        target_pattern = r'(<blockquote>)'
        if not re.search(target_pattern, content):
            print(f"  [SKIP] No target div/blockquote found in {html_path}")
            return False

    # Create Injection Block
    # We embed the JP content in a hidden div
    safe_jp = format_japanese_text(jp_content)
    
    injection = f"""
<!-- LANGUAGE TOGGLE INJECTED start -->
<div class="lang-toggle-bar" style="margin-bottom: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; text-align: right;">
    <button id="btn-pt" onclick="toggleLang('pt')" style="padding: 5px 10px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 3px;">Português</button>
    <button id="btn-jp" onclick="toggleLang('jp')" style="padding: 5px 10px; cursor: pointer; background: #ddd; color: #333; border: none; border-radius: 3px;">Original (JP)</button>
</div>

<div id="jp-content" style="display: none; font-family: 'Yu Mincho', serif; font-size: 1.1em; line-height: 1.8; background: #fff; padding: 20px; border: 1px solid #eee;">
    {safe_jp}
</div>

<script>
function toggleLang(lang) {{
    const ptContent = document.querySelector('.translated-content') || document.querySelector('blockquote');
    const jpContent = document.getElementById('jp-content');
    const btnPt = document.getElementById('btn-pt');
    const btnJp = document.getElementById('btn-jp');

    if (lang === 'jp') {{
        ptContent.style.display = 'none';
        jpContent.style.display = 'block';
        btnPt.style.background = '#ddd';
        btnPt.style.color = '#333';
        btnJp.style.background = '#4CAF50';
        btnJp.style.color = 'white';
    }} else {{
        ptContent.style.display = 'block';
        jpContent.style.display = 'none';
        btnPt.style.background = '#4CAF50';
        btnPt.style.color = 'white';
        btnJp.style.background = '#ddd';
        btnJp.style.color = '#333';
    }}
}}
</script>
<!-- LANGUAGE TOGGLE INJECTED end -->
"""
    
    # Inject
    new_content = re.sub(target_pattern, injection + r'\1', content, count=1)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    index = load_data()
    translations = load_translations()
    
    count = 0
    total = 0
    
    for item in index:
        url = item.get('url')
        if not url: continue
        
        # Determine local path
        # URL is relative to root? No, usually relative to something else or absolute in web server terms
        # But we are in root. let's check.
        # url examples: "search1/shi/joron24.html"
        
        local_path = os.path.join(PROJECT_ROOT, url)
        # Handle query params if any (shouldn't be in static paths but good to be safe)
        if '?' in local_path: local_path = local_path.split('?')[0]
        
        jp_text = get_japanese_content(item, translations)
        if not jp_text:
            # print(f"No JP text for {item['id']}")
            continue

        if inject_toggle(local_path, jp_text):
            count += 1
            print(f"Injected {item['id']} -> {local_path}")
        
    print(f"Finished. Injected {count} files.")

if __name__ == "__main__":
    main()
