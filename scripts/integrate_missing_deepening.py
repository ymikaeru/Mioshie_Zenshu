import json
import re
import os

JSON_FILE = 'gosanka/yamato_full.json'
MARKDOWN_FILE = 'Data/missing_deepening.md'

def parse_markdown_translations(filepath):
    print(f"Lendo traduções de: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator ---
    # Regex to split but keep the content sane
    # The format is ## [ID] ... content ... ---
    
    # We can split by "## " at start of line
    chunks = re.split(r'(^|\n)##\s+(\d+)\.', content)
    
    translations = {}
    
    # chunks[0] = empty/preface
    # chunks[1] = newline/sep
    # chunks[2] = ID
    # chunks[3] = Content
    # ...
    
    for i in range(2, len(chunks), 3):
        pid = int(chunks[i])
        block = chunks[i+1]
        
        # Extract fields using Regex
        # 🍃 Kigo (A Estação e o Clima): [Content]
        kigo_match = re.search(r'\*\*🍃 Kigo.*?\*\*[:\s]*(.*?)(?=\n\n\*\*|\Z)', block, re.DOTALL)
        kototama_match = re.search(r'\*\*🎵 Kototama.*?\*\*[:\s]*(.*?)(?=\n\n\*\*|\Z)', block, re.DOTALL)
        deepening_match = re.search(r'\*\*🏔️ A Profundidade.*?\*\*[:\s]*(.*?)(?=\n\n---|\Z)', block, re.DOTALL)
        
        # Also Extract Translation if needed (though user mainly asked for Deepening/Kigo context)
        # "Tradução Artística:" ... "[Text]"
        # translation_match = re.search(r'\*\*Tradução Artística:\*\*\s*"(.*?)"', block, re.DOTALL)
        
        trans_data = {
            'kigo': kigo_match.group(1).strip() if kigo_match else "",
            'kototama': kototama_match.group(1).strip() if kototama_match else "",
            'deepening': deepening_match.group(1).strip() if deepening_match else ""
        }
        
        # Clean up Markdown bolding or extra spaces if any
        # Usually checking if they are not empty is enough
        
        if trans_data['deepening']:
            translations[pid] = trans_data
    
    return translations

def main():
    print("--- INTEGRANDO TRADUÇÕES ---")
    
    translations = parse_markdown_translations(MARKDOWN_FILE)
    print(f"Traduções parseadas: {len(translations)}")
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    
    if 'sections' in data:
        for section in data['sections']:
            for poem in section['poems']:
                pid = poem['number']
                if pid in translations:
                    t = translations[pid]
                    
                    # Update fields
                    # Only update if existing is empty or we want to overwrite?
                    # Since we targeted missing ones, overwrite is safe/expected.
                    
                    if t['kigo']: poem['kigo'] = t['kigo']
                    if t['kototama']: poem['kototama'] = t['kototama']
                    if t['deepening']: poem['deepening'] = t['deepening']
                    
                    updated_count += 1
    
    print(f"Atualizando arquivo JSON: {updated_count} poemas modificados.")
    
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print("Sucesso!")

if __name__ == "__main__":
    main()
