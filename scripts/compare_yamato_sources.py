import json
import re

json_path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/Data/poems.json'
md_path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'

with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Extract original Japanese text from MD to match
# Pattern: **Original:** (Japanese text)
md_originals = re.findall(r'\*\*Original:\*\*\s*(.+?)(?=\*\*Leitura:|$)', md_content)
# Clean up whitespace
md_originals_clean = [s.strip().replace(' ', '').replace('　', '') for s in md_originals]
md_orig_set = set(md_originals_clean)

missing_in_md = []

for entry in json_data:
    orig = entry.get('original', '')
    # Extract just the Japanese part if it contains markup (the json snippet showed some markup?)
    # The snippet showed: "雨はれて　露もしとどの..."
    
    # We need to clean the JSON original text similarly
    # Remove "**Leitura:**..." if present in key
    orig_clean = orig.split('**Leitura:**')[0].strip().replace(' ', '').replace('　', '')
    
    if orig_clean and orig_clean not in md_orig_set:
        missing_in_md.append(entry.get('title', 'No Title'))

print(f"Total Markdown matching originals found: {len(md_orig_set)}")
print(f"JSON entries missing from Markdown: {len(missing_in_md)}")
if missing_in_md:
    print(f"First 10 missing titles: {missing_in_md[:10]}")
