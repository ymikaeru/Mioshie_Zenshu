import re
import json
import os

md_path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'
output_path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/gosanka/yamato_full.json'

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        "preface": {
            "title_pt": "Prefácio",
            "title_jp": "はしがき",
            "content_pt": [],
            "content_jp": []
        },
        "sections": []
    }

    # Extract Preface
    # Strategy: Find "## Prefácio" or "📂 SEÇÃO: Prefácio"
    # The cleaned file has: # 📂 SEÇÃO: Prefácio (はしがき)
    # Content follows until next # 📂 SEÇÃO
    
    preface_match = re.search(r'# 📂 SEÇÃO: Prefácio.*?\n(.*?)(?=\n# 📂 SEÇÃO:)', content, re.DOTALL)
    if preface_match:
        preface_text = preface_match.group(1).strip()
        # Split into PT and JP blocks if possible, or just dump for now.
        # Looking at file structure, it usually has "Original:" or just text.
        # Let's assume paragraphs. 
        # For this specifc request, user needs PT translation.
        # I'll store the raw paragraphs for now, but refine if I see specific markers.
        data['preface']['content_pt'] = [p for p in preface_text.split('\n\n') if p.strip()]

    # Extract Sections
    # Regex for sections: # 📂 SEÇÃO: (Title PT) \((Title JP)\) ... or variations
    section_split = re.split(r'(^|\n)# 📂 SEÇÃO:', content)
    
    # section_split[0] is everything before first section (header metadata etc)
    # section_split[1] is empty (due to capture group)
    # section_split[2] is first section Title... + content
    # ...
    
    # Actually, simpler to iterate matches
    raw_sections = re.findall(r'(# 📂 SEÇÃO:.*?(?=\n# 📂 SEÇÃO:|$))', content, re.DOTALL)
    
    current_poem_number = 0 # To track continuity
    
    for raw_sec in raw_sections:
        # Parse Title
        title_line_match = re.match(r'# 📂 SEÇÃO:\s*(.*)', raw_sec)
        if not title_line_match:
            continue
            
        full_title = title_line_match.group(1).strip()
        # Parse "Title (JP Title)"
        title_match = re.match(r'(.*?)\s*\((.*?)\)', full_title)
        if title_match:
            sec_title_pt = title_match.group(1).strip()
            sec_title_jp = title_match.group(2).strip()
        else:
            sec_title_pt = full_title
            sec_title_jp = ""
            
        # Ignore Prefácio in this loop if handled separately, or include it?
        if "Prefácio" in sec_title_pt:
            continue

        section_obj = {
            "title_pt": sec_title_pt,
            "title_jp": sec_title_jp,
            "poems": []
        }

        # Find poems in this section
        # Poem format: ## Number. Title
        poem_chunks = re.split(r'\n## (\d+)\.', raw_sec)
        # chunk[0] is section intro text (if any)
        # chunk[1] is poem number
        # chunk[2] is poem content (Title \n **Original:** ...)
        
        # Iterate chunks in pairs (num, content)
        for i in range(1, len(poem_chunks), 2):
            p_num = poem_chunks[i]
            p_content = poem_chunks[i+1]
            
            # Extract Title (first line of p_content)
            p_lines = p_content.split('\n', 1)
            p_title = p_lines[0].strip()
            p_body = p_lines[1] if len(p_lines) > 1 else ""
            
            # Extract fields
            # **Original:** ... **Leitura:** ...
            original_match = re.search(r'\*\*Original:\*\*\s*(.*?)\s*\*\*Leitura:\*\*\s*(.*)', p_body)
            original = original_match.group(1).strip() if original_match else ""
            reading = original_match.group(2).strip() if original_match else ""
            
            # **Tradução Artística:** "..."
            trans_match = re.search(r'\*\*Tradução Artística:\*\*\s*["\']?(.*?)["\']?\s*(?=\*\*|$)', p_body, re.DOTALL)
            translation = trans_match.group(1).strip() if trans_match else ""
            
            # **🍃 Kigo ...:** ...
            kigo_match = re.search(r'\*\*.*?Kigo.*?\*\*[:]?\s*(.*?)\s*(?=\*\*|$)', p_body, re.DOTALL)
            kigo = kigo_match.group(1).strip() if kigo_match else ""

            # **🎵 Kototama ...:** ...
            kototama_match = re.search(r'\*\*.*?Kototama.*?\*\*[:]?\s*(.*?)\s*(?=\*\*|$)', p_body, re.DOTALL)
            kototama = kototama_match.group(1).strip() if kototama_match else ""

            # **🏔️ A Profundidade ...:** ...
            deep_match = re.search(r'\*\*.*?Profundidade.*?\*\*[:]?\s*(.*?)\s*(?=\n|$)', p_body, re.DOTALL)
            # Or capture until next header or end of string
            deepening = deep_match.group(1).strip() if deep_match else ""
            
            # Fallback for deepening if it spans lines
            if not deepening:
                 deep_start = p_body.find('Profundidade')
                 if deep_start != -1:
                     deepening = p_body[deep_start:].split('**', 1)[-1].lstrip(':').strip()

            poem_obj = {
                "number": int(p_num),
                "title": p_title,
                "original": original,
                "reading": reading,
                "translation": translation,
                "kigo": kigo,
                "kototama": kototama,
                "deepening": deepening
            }
            
            section_obj["poems"].append(poem_obj)
            current_poem_number = int(p_num)
            
        data["sections"].append(section_obj)
        
    # Serialize
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Generated {output_path} with {len(data['sections'])} sections.")

if __name__ == "__main__":
    parse_markdown(md_path)
