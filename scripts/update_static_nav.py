
import json
import os
import glob
from bs4 import BeautifulSoup
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'Data', 'teachings_translated.json')
FILETOP_DIR = os.path.join(BASE_DIR, 'filetop')
NAV_FILE = os.path.join(BASE_DIR, '3.html')

def get_display_title(item):
    # Priority 1: Markdown Header in PT content
    content = item.get('content_ptbr') or item.get('content_pt')
    if content:
        match = re.search(r'^#+\s+(.*)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    
    # Priority 2: Title field
    title = item.get('title')
    if title and title != "(Sem Título)":
        return title
        
    # Priority 3: Japanese Title
    title_jp = item.get('title_jp')
    if title_jp:
        return f"{title_jp} (JP)"
        
    return item.get('source_file') or "Sem Título"

def main():
    print("Mapping HTML files...")
    file_map = {}
    # Find all .html files
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".html"):
                abspath = os.path.join(root, file)
                relpath = os.path.relpath(abspath, BASE_DIR)
                file_map[file] = relpath

    print(f"Mapped {len(file_map)} files.")

    print("Loading JSON data...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Prepare data for sorting
    items = []
    for item in data:
        title = get_display_title(item)
        source = item.get('source_file')
        if not source: continue
        
        # Resolve path
        if source in file_map:
            # Path relative to filetop/ directory where indices will live
            # file_map[source] is relative to BASE_DIR
            # we need relative to BASE_DIR/filetop
            full_rel_path = file_map[source] # e.g. "search1/a/aaiga1.html"
            # rel from filetop: ../search1/a/aaiga1.html
            link_path = os.path.relpath(os.path.join(BASE_DIR, full_rel_path), FILETOP_DIR)
        else:
            link_path = "#" # File not found?
        
        items.append({
            'title': title,
            'link': link_path,
            'original_source': item.get('source', ''),
            'date': item.get('date', ''),
            'sort_key': title.upper()
        })

    # Sort
    items.sort(key=lambda x: x['title'].lower().strip())

    # Group by Letter
    groups = {}
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        groups[char] = []
    groups['#'] = []

    for item in items:
        first_char = item['title'][0].upper()
        if 'A' <= first_char <= 'Z':
            groups[first_char].append(item)
        else:
            groups['#'].append(item)

    # Generate Index Pages
    template_start = """<html>
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
<title>Index {letter}</title>
<link href="../style1.css" rel="stylesheet" type="text/css"/>
</head>
<body bgcolor="#E9FEDA">
<div align="center"><h1>Índice - {letter}</h1>
<table bgcolor="#EFFFE6" border="1" bordercolor="#C0C0C0" bordercolordark="#C0C0C0" bordercolorlight="#E9FEDA" cellpadding="2" cellspacing="0" width="100%">
<tr>
<td bgcolor="#008080" width="50%"><p align="center"><font color="#FFFFFF">TÍTULO</font></p></td>
<td bgcolor="#008080" width="30%"><p align="center"><font color="#FFFFFF">ARQUIVO</font></p></td>
<td align="center" bgcolor="#008080" width="20%"><p align="center"><font color="#FFFFFF" size="3">DATA</font></p></td>
</tr>
"""
    template_end = """</table></div></body></html>"""

    for letter, group_items in groups.items():
        filename = f"idx_pt_{letter}.html"
        if letter == '#': filename = "idx_pt_09.html"
        
        content = template_start.format(letter=letter)
        for it in group_items:
            content += f"""<tr>
<td><a href="{it['link']}" target="main">{it['title']}</a></td>
<td>{it['original_source']}</td>
<td align="center">{it['date'] or ''}</td>
</tr>"""
        content += template_end
        
        with open(os.path.join(FILETOP_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filename} ({len(group_items)} items)")

    print("Skipping 3.html update (handled manually).")
    return

def locale_aware_sort(item):
    # Dummy for now, standard sort is okay for basic usage
    return item['title']

if __name__ == "__main__":
    main()
