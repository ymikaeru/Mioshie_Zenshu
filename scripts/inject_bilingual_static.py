
import json
import os
import re
from bs4 import BeautifulSoup, Tag, NavigableString

# Config
INDEX_FILE = 'Data/advanced_search_index.json'
DATA_DIR = 'Data'
PROJECT_ROOT = '.' 

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
    # Simple formatting: plain text to basic HTML paragraphs if needed
    # But usually the source content is already somewhat formatted or just plain text.
    # We will wrap it in a div.
    # Replace newlines with <br> for simple display
    cleaned = re.sub(r'(</div>|</body>|</html>)+\s*$', '', text, flags=re.IGNORECASE).strip()
    if '\n' in cleaned:
        return cleaned.replace('\n', '<br>')
    else:
        return cleaned.replace('。', '。<br><br>')

def resolve_path(url):
    possibilities = [
        url,
        os.path.join('sasshi', url),
        os.path.join('search1', url),
        os.path.join('filetop', url),
        os.path.join('search1/situmon', url),
        os.path.join('search1/shi', url)
    ]
    for p in possibilities:
        if os.path.exists(p) and os.path.isfile(p):
            return p
    return None

def inject_bilingual_features(html_path, jp_content):
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        print(f"  [ERROR] Reading {html_path}: {e}")
        return False

    # 1. CLEANUP: Remove old injected elements
    print(f"    Cleaning {html_path}...")
    # Remove all toggle bars
    for el in soup.find_all(class_='lang-toggle-bar'):
        el.decompose()
    
    # Remove all jp-content divs (could be multiple if script ran multiple times)
    for el in soup.find_all(id='jp-content'):
        el.decompose()
        
    # Remove old scripts containing toggleLang
    # checking all script tags is safer
    scripts = soup.find_all('script')
    for s in scripts:
        if s.string and 'function toggleLang' in s.string:
            s.decompose()
    
    # Remove potential "LANGUAGE TOGGLE INJECTED" comments? 
    # (Checking comments is harder but toggle bars usually catch the visual part)


    # 2. IDENTIFY CONTENT CONTAINER
    # Priority: #pt-content -> .content-wrapper -> body
    content_container = soup.find(id='pt-content')
    
    if not content_container:
        # We need to create it and move content inside.
        # Strategy: Find the main content wrapper or body, and assume everything 
        # that ISN'T a script/style/nav is content.
        
        main_wrapper = soup.find(class_='content-wrapper') or soup.find(id='main') or soup.body
        
        if not main_wrapper:
            print("  [SKIP] No body tag found.")
            return False
            
        # Create new pt-content div
        new_pt_div = soup.new_tag('div', id='pt-content')
        
        # Move children of main_wrapper into new_pt_div
        # Be careful not to break iteration by modifying list while iterating
        children_to_move = []
        for child in main_wrapper.contents:
             # Skip our own injected stuff if it wasn't cleaned properly (safety)
            if isinstance(child, Tag) and child.get('id') == 'jp-content': continue
            children_to_move.append(child)
            
        for child in children_to_move:
            new_pt_div.append(child)
            
        main_wrapper.append(new_pt_div)
        content_container = new_pt_div

    # Ensure container style allows side-by-side
    # We will control layout via a parent class or inline style manipulation in JS
    
    # 3. PREPARE JAPANESE CONTENT
    jp_div = soup.new_tag('div', id='jp-content')
    jp_div['style'] = 'display: none; background: #fff; padding: 20px; font-family: "Yu Mincho", serif;'
    
    # We already formatted text as string, parse it to soup nodes? 
    # Or just set innerHTML equivalent.
    formatted_jp = format_japanese_text(jp_content)
    # Parse as HTML fragments to be safe
    jp_soup = BeautifulSoup(formatted_jp, 'html.parser')
    jp_div.append(jp_soup)
    
    # Insert jp_div AFTER pt_content
    content_container.insert_after(jp_div)

    # 4. INJECT CSS & JS
    head = soup.head
    if not head:
        head = soup.new_tag('head')
        soup.html.insert(0, head)

    style_tag = soup.new_tag('style')
    style_tag.string = """
    .lang-toggle-bar {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: #f8f9fa;
        border-bottom: 1px solid #ddd;
        padding: 10px 20px;
        text-align: right;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        grid-column: 1 / -1; /* Ensure full width in grid mode */
    }
    .lang-btn {
        padding: 8px 16px;
        border: 1px solid #ccc;
        background: white;
        cursor: pointer;
        border-radius: 4px;
        font-size: 14px;
        transition: all 0.2s;
    }
    .lang-btn:hover { background: #eee; }
    .lang-btn.active {
        background: #2E7D32;
        color: white;
        border-color: #1b5e20;
    }
    /* Compare Mode Styles */
    body.compare-mode .content-wrapper, 
    body.compare-mode #main,
    body.compare-mode body /* fallback */ {
        max-width: 95% !important;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    body.compare-mode #pt-content,
    body.compare-mode #jp-content {
        display: block !important;
        height: 85vh; /* approximate viewport height minus header */
        overflow-y: auto;
        padding: 20px;
        border: 1px solid #eee;
        border-radius: 5px;
        background: #fff;
    }
    /* Hide header/footer in compare mode if desired, or keep them */
    """
    if head:
        head.append(style_tag)

    # 5. INJECT TOGGLE BAR
    toggle_bar = soup.new_tag('div', attrs={'class': 'lang-toggle-bar'})
    
    btns = [
        ('btn-pt', 'Português', "toggleLang('pt')"),
        ('btn-jp', 'Original (JP)', "toggleLang('jp')"),
        ('btn-compare', 'Comparar', "toggleLang('compare')")
    ]
    
    for bib, text, action in btns:
        b = soup.new_tag('button', id=bib, attrs={'class': 'lang-btn', 'onclick': action})
        b.string = text
        if bib == 'btn-pt': b['class'] = 'lang-btn active'
        toggle_bar.append(b)

    # Insert toggle bar at the start of body
    if soup.body:
        soup.body.insert(0, toggle_bar)

    # 6. INJECT SCRIPT
    script_tag = soup.new_tag('script')
    script_tag.string = """
    function toggleLang(mode) {
        const pt = document.getElementById('pt-content');
        const jp = document.getElementById('jp-content');
        const body = document.body;
        
        // Buttons
        const btnPt = document.getElementById('btn-pt');
        const btnJp = document.getElementById('btn-jp');
        const btnCompare = document.getElementById('btn-compare');
        
        // Reset ALL classes first
        btnPt.classList.remove('active');
        btnJp.classList.remove('active');
        btnCompare.classList.remove('active');
        body.classList.remove('compare-mode');
        
        // Default Styles reset (in case they were inline changed)
        if(pt) { pt.style.display = ''; pt.style.height = ''; pt.style.overflowY = ''; }
        if(jp) { jp.style.display = 'none'; jp.style.height = ''; jp.style.overflowY = ''; }

        if (mode === 'pt') {
            if(pt) pt.style.display = 'block';
            if(jp) jp.style.display = 'none';
            btnPt.classList.add('active');
        } 
        else if (mode === 'jp') {
            if(pt) pt.style.display = 'none';
            if(jp) jp.style.display = 'block';
            btnJp.classList.add('active');
        }
        else if (mode === 'compare') {
            body.classList.add('compare-mode');
            if(pt) {
                pt.style.display = 'block';
                // Inline styles for scroll are handled by CSS class but let's ensure
            }
            if(jp) {
                jp.style.display = 'block';
            }
            btnCompare.classList.add('active');
        }
    }
    """
    if soup.body:
        soup.body.append(script_tag)

    # Save
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    return True

def main():
    index = load_data()
    translations = load_translations()
    
    count = 0
    MAX_ITEMS = 5000 # Safety limit
    
    # Filter for items that have a URL (static file) AND Japanese content available
    targets = []
    
    for item in index:
        url = item.get('url')
        if not url: continue
        
        # Resolve full path
        path = resolve_path(url)
        if not path:
            print(f"Skipping {url} (Not found)")
            continue
            
        jp = get_japanese_content(item, translations)
        if not jp:
            continue
            
        targets.append((path, jp))

    print(f"Found {len(targets)} static pages to inject.")
    
    # Process
    for path, jp in targets[:MAX_ITEMS]:
        print(f"Injecting {path}...")
        if inject_bilingual_features(path, jp):
            count += 1
            
    print(f"Done. Injected {count} pages.")

if __name__ == "__main__":
    main()
