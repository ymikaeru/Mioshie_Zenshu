
import re
import json

def parse_poems(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by separator, ignoring the preface
    sections = content.split('---')
    poems = []

    for section in sections:
        # Regex extraction - handle '1\.' or '1.'
        title_match = re.search(r'##\s+\d+(\\)?\.\s+(.+)', section)
        if not title_match:
            # Try looser match if specific format fails
            title_match = re.search(r'##\s+\d+.*?\s+(.+)', section)
        
        if not title_match:
            print(f"Skipping section (no title match): {section[:50]}...")
            continue
        
        title = title_match.group(2) if len(title_match.groups()) >= 2 else title_match.group(1)
        title = title.strip()
        
        original_match = re.search(r'\*\*Original:\*\*\s+(.+)', section)
        original = original_match.group(1).strip() if original_match else ""

        leitura_match = re.search(r'\*\*Leitura:\*\*\s+(.+)', section)
        leitura = leitura_match.group(1).strip() if leitura_match else ""
        
        # Translation
        # Regex looks for Translation header, captures until Kigo header or end of section if Kigo is missing
        translation_match = re.search(r'\*\*Tradução Artística:\*\*\s+([\s\S]+?)(?=\*\*🍃|\*\*🎵|\*\*🏔️|$)', section)
        translation = translation_match.group(1).strip() if translation_match else ""

        # Kigo
        kigo_match = re.search(r'\*\*🍃 Kigo \(A Estação e o Clima\):\*\*\s+([\s\S]+?)(?=\*\*🎵|\*\*🏔️|$)', section)
        kigo = kigo_match.group(1).strip() if kigo_match else ""

        # Kototama
        kototama_match = re.search(r'\*\*🎵 Kototama \(A Sonoridade\):\*\*\s+([\s\S]+?)(?=\*\*🏔️|$)', section)
        kototama = kototama_match.group(1).strip() if kototama_match else ""

        # Depth/Meaning
        depth_match = re.search(r'\*\*🏔️ A Profundidade \(Lição Espiritual\):\*\*\s+([\s\S]+?)(?=$)', section)
        depth = depth_match.group(1).strip() if depth_match else ""

        # Fallback: if 'meaning' was previously just capturing depth, now we have structured data.
        # But if some poems don't have these specific headers, we might need a fallback.
        # However, based on user input, we want these specific sections.

        poems.append({
            "title": title,
            "original": original,
            "reading": leitura,
            "translation": translation,
            "kigo": kigo,
            "kototama": kototama,
            "meaning": depth 
        })

    return poems

if __name__ == "__main__":
    input_file = "Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md"
    output_file = "Data/poems.json"
    
    poems = parse_poems(input_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(poems, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(poems)} poems into {output_file}")
