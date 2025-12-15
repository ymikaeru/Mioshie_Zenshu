
import json
import os
import glob
from bs4 import BeautifulSoup
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(BASE_DIR, 'Data', 'teachings_manifest.json')
DATA_DIR = os.path.join(BASE_DIR, 'Data')
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

# Mapping Dictionary
TERM_MAPPING = {
    '栄光': 'Eikou',
    '救世': 'Kyusei',
    '光明世界': 'Koumyou Sekai',
    '地上天国': 'Chijo Tengoku',
    '東方の光': 'Touhou no Hikari',
    '明日の医術': 'Ashita no Ijutsu',
    '天国の福音': 'Tengoku no Fukuin',
    '文明の創造': 'Bunmei no Souzou',
    'Igaku Kakumei Sho': 'Igaku Kakumei no Sho',
    '全集': 'Zenshu',
    '光への道': 'Hikari e no Michi',
    '霊界叢談': 'Reikai Soudan',
    'アメリカを救う': 'America wo Sukuu',
    '観音の光': 'Kannon no Hikari',
    '日本医術講義録': 'Nihon Ijutsu Kougiroku',
    '講話': 'Kouwa',
    '御垂示': 'Gosuiji',
    '号': ' Gou',     # Issue
    '編': ' Hen',     # Volume/Part
    '書': ' Sho',     # Book
    '版': ' Ban',     # Edition
    '昭和': 'Showa ',
    '年': ' Nen',
    '月': ' Gatsu',
    '日': ' Nichi',
    '未発表': 'Mihappyou',
    '執筆': 'Shippitsu',
    '付録': 'Furoku',
    '再版': 'Saiban', # Reprint
    '初版': 'Shohan', # First edition
    '読売新聞': 'Yomiuri Shimbun',
    '岡田茂吉': 'Okada Mokichi',
    '結核問題と其解決策': 'Kekkaku Mondai to Sono Kaiketsusaku',
    '新日本医術': 'Shin Nihon Ijutsu',
    '世界救世教': 'Sekai Kyuseikyo',
    '奇蹟集': 'Kisekishu',
    '広告文': 'Kokokubun',
    '新稿': 'Shinko',
    # Portuguese Mappings
    'Ashita no Ijutsu': 'Ashita no Ijutsu',
    'Coletânea de Teses do Mestre Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Ensaios do Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'Ensaios de Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'A Questão da Tuberculose e sua Solução': 'Kekkaku Mondai to Sono Kaiketsusaku',
    'O Problema da Tuberculose e sua Solução': 'Kekkaku Mondai to Sono Kaiketsusaku',
    'Livro da Nova Arte Médica Japonesa': 'Shin Nihon Ijutsu',
    'Nova Arte Médica Japonesa': 'Shin Nihon Ijutsu',
    'Palestras de Kannon': 'Kannon Koza',
    'O Movimento de Kannon e sua Declaração': 'Kannon Undo to Sono Sengen',
    'Crônicas de uma Peregrinação Sagrada': 'Seichi Junrei Kiroku',
    'Relatos de Graças': 'Kiseki Shu',
    'Luz da Sabedoria Divina': 'Hikari no Chie',
    'Curso de Johrei': 'Jorei Koza',
    'Guia de Difusão': 'Fukyu no Tebiki',
    'Evangelho do Céu': 'Tengoku no Fukuin',
    'Criação da Civilização': 'Bunmei no Sozo',
    'Alicerce do Paraíso': 'Chijo Tengoku',
    'A Face da Verdade': 'Shinjitsu no Gao', 
    'Jornal Eikou': 'Eikou',
    'Jornal Kyusei': 'Kyusei',
    'Jornal Hikari': 'Hikari',
    'O Pão Nosso de Cada Dia': 'Hibi no Kate'
}

def translate_source(text):
    if not text:
        return text
    
    translated = text
    # Sort keys by length descending to replace longer phrases first
    sorted_keys = sorted(TERM_MAPPING.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        val = TERM_MAPPING[key]
        if key in translated:
            translated = translated.replace(key, val)
    return translated

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

    print("Loading JSON data from manifest...")
    data = load_all_translations(MANIFEST_PATH)

    # Prepare data for sorting
    items = []
    for item in data:
        title = get_display_title(item)
        source = item.get('source_file')
        if not source: continue
        
        # Resolve path
        if source in file_map:
            # Path relative to filetop/ directory where indices will live
            full_rel_path = file_map[source] # e.g. "search1/a/aaiga1.html"
            # rel from filetop: ../search1/a/aaiga1.html
            link_path = os.path.relpath(os.path.join(BASE_DIR, full_rel_path), FILETOP_DIR)
        else:
            link_path = "#" # File not found?
        
        # Translate source name and TITLE
        original_source = item.get('source', '')
        translated_source_name = translate_source(original_source)
        
        # Translate Title too as per user request
        translated_title = translate_source(title)

        items.append({
            'title': translated_title,
            'link': link_path,
            'original_source': translated_source_name,
            'date': item.get('date', ''),
            'sort_key': translated_title.upper()
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
<td bgcolor="#008080" width="30%"><p align="center"><font color="#FFFFFF">FONTE</font></p></td>
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
