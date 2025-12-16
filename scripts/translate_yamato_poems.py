
import json
import time
import os
import re
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
# API KEY fornecida pelo usuário
API_KEY = "AIzaSyC3e_S5y_ZOAMn_qyqxFoCEmD1TPR-RxUU" 
HTML_FILE = 'gosanka/yamato.html'
MARKDOWN_FILE = 'Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'

# --- CONFIGURAÇÃO DA IA ---
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

PROMPT_SISTEMA = """
Você é um tradutor especialista em literatura japonesa e espiritualidade, focado na obra de Mokichi Okada (Meishu-Sama).
Sua tarefa é traduzir poemas (Waka/Tanka) do japonês para o português, seguindo o "Modelo de Profundidade Máxima".

**Regras de Estilo e Conteúdo:**
1.  **Tradução Artística:** Não faça traduções literais. Capte a "alma" do poema e reescreva em português poético, fluido e elevado.
2.  **Análise Trindade:** Para CADA poema, você deve fornecer:
    *   **Kigo (A Estação e o Clima):** Identifique a palavra de estação (Kigo) ou o sentimento sazonal/atmosférico.
    *   **Kototama (A Sonoridade):** Analise os sons (rimas, aliterações, ritmo) e o "espírito das palavras" japonesas relevantes.
    *   **A Profundidade (Lição Espiritual):** O mais importante. Explique o ensinamento espiritual oculto (Filosofia de Mokichi Okada), conectando a natureza/arte à Lei Divina, Makoto (Sinceridade), ou Salvação.
3.  **Formatação:** Siga estritamente o template abaixo. Use emojis exatos.

**Template de Saída para CADA Poema:**

## [Número]. [Título Criativo em Português]

**Original:** [Texto Japonês] **Leitura:** [Romaji]

**Tradução Artística:**

"[Texto da Tradução em Português]"

**🍃 Kigo (A Estação e o Clima):** [Análise]

**🎵 Kototama (A Sonoridade):** [Análise]

**🏔️ A Profundidade (Lição Espiritual):** [Análise]

---

**Instruções de Batch:**
Separe cada análise com `---`.
"""

def parse_html_structure(path):
    print(f"Lendo estrutura do HTML: {path}")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    structure = [] # List of dicts: {'type': 'poem'|'category', 'id': int, 'content': str, 'original': str, 'reading': str}
    
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if not cols: continue
            
            # Category Check
            text_content = row.get_text(strip=True)
            bold = row.find('strong')
            first_col_text = cols[0].get_text(strip=True)
            
            if not first_col_text.isdigit() and bold:
                 cat_title = bold.get_text(strip=True).replace('　', ' ')
                 if cat_title and "昭和" not in cat_title and "目次" not in cat_title:
                     structure.append({'type': 'category', 'title': cat_title})
            
            # Poem Check
            poem_num_text = cols[0].get_text(strip=True)
            if poem_num_text.isdigit():
                poem_id = int(poem_num_text)
                content_col = cols[1]
                fonts = content_col.find_all('font')
                original_text = ""
                reading_text = ""
                
                for ft in fonts:
                    fs = ft.get('size')
                    ft_text = ft.get_text(strip=True)
                    if fs == '3':
                        original_text = ft_text
                    elif fs == '1' and not reading_text:
                        reading_text = ft_text
                
                if not original_text and len(fonts) > 0:
                    original_text = fonts[-1].get_text(strip=True)

                original_text = original_text.replace('\n', '').strip()
                reading_text = reading_text.replace('\n', '').strip()

                structure.append({
                    'type': 'poem',
                    'id': poem_id,
                    'original': original_text,
                    'reading': reading_text
                })
    return structure

def parse_existing_markdown(path):
    print(f"Lendo Markdown existente: {path}")
    if not os.path.exists(path):
        return {}
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by poems using Regex lookahead for "## [Numbers]"
    # This might is tricky if logic is loose. 
    # Let's split by `## ` and check if it starts with number.
    
    parts = re.split(r'(^|\n)##\s+(\d+)', content)
    # parts[0] = intro
    # parts[1] = newline/empty
    # parts[2] = ID
    # parts[3] = Content including title ...
    
    poem_map = {} # id -> full_content_string
    
    # We might lose the first part (preface), need to save it.
    intro = parts[0]
    
    # Starting from index 1, we have groups of 3 (separator, id, content)
    # Actually re.split with groups returns the groups.
    
    # Iterate 
    current_id = None
    
    # Logic: 
    # The split creates: [pre-match, group1(sep), group2(id), post-match, group1, group2, post...]
    
    # Let's use finditer for safety to capture positions
    matches = list(re.finditer(r'(^|\n)##\s+(\d+)(?:\.|\\.)\s+(.*?)(?=(?:\n##\s+\d+)|\Z)', content, re.DOTALL))
    
    for m in matches:
        p_id = int(m.group(2))
        full_block = m.group(0).strip() # "## 123. Title\n content..."
        poem_map[p_id] = full_block

    # Also capture Preface (everything before first poem)
    first_match_start = matches[0].start() if matches else len(content)
    preface = content[:first_match_start]
    
    return poem_map, preface

def translate_poems(poems_to_translate):
    translations = {}
    BATCH_SIZE = 5
    
    for i in range(0, len(poems_to_translate), BATCH_SIZE):
        batch = poems_to_translate[i : i+BATCH_SIZE]
        print(f"Traduzindo batch {i//BATCH_SIZE + 1} ({batch[0]['id']} - {batch[-1]['id']})...")
        
        prompt_content = ""
        for p in batch:
            prompt_content += f"Poema {p['id']}:\nOriginal: {p['original']}\nLeitura: {p['reading']}\n\n"
        
        full_prompt = f"{PROMPT_SISTEMA}\n\n**POEMAS:**\n{prompt_content}"
        
        try:
            response = model.generate_content(full_prompt)
            text = response.text
            
            # Parse back response to individual poems
            # Assuming ## [ID] format
            
            # Simple split by ## [Numbers]
            found_parts = re.split(r'##\s+(\d+)', text)
            
            # found_parts[0] usually empty or trash
            # found_parts[1] = ID, found_parts[2] = content
            
            for j in range(1, len(found_parts), 2):
                pid = int(found_parts[j])
                pcontent = found_parts[j+1].strip()
                # Reconstruct header
                header_line = re.search(r'^\s*\.?\s*(.+?)\n', pcontent)
                title = header_line.group(1).strip() if header_line else "Sem Título"
                
                # Careful: The API might return just the body or include the header line.
                # Our Template says: ## [Num]. [Title]
                # So the regex split consumes ## [Num]
                # The pcontent starts with ". [Title]" or " [Title]"
                
                # Clean up title line from content
                # pcontent usually starts with ". O Título\n\n**Original:..."
                
                final_block = f"## {pid}. {pcontent}"
                translations[pid] = final_block
                
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro no batch: {e}")
            
    return translations

def main():
    print("--- INICIANDO RECONSTRUÇÃO ---")
    
    # 1. Parse HTML Structure (The Truth of Order)
    html_structure = parse_html_structure(HTML_FILE)
    print(f"Estrutura HTML carregada: {len(html_structure)} itens.")
    
    # 2. Parse Existing Markdown (The Database)
    poem_map, preface = parse_existing_markdown(MARKDOWN_FILE)
    print(f"Traduções existentes carregadas: {len(poem_map)} poemas.")
    
    # 3. Identify Missing
    html_poem_ids = [item['id'] for item in html_structure if item['type'] == 'poem']
    missing_ids = [pid for pid in html_poem_ids if pid not in poem_map]
    print(f"Poemas faltando: {len(missing_ids)}")
    
    missing_items = [item for item in html_structure if item['type'] == 'poem' and item['id'] in missing_ids]
    
    # 4. Translate Missing
    if missing_items:
        print("Iniciando tradução dos faltantes...")
        new_translations = translate_poems(missing_items)
        poem_map.update(new_translations)
    
    # 5. Rebuild File
    print("Reconstruindo arquivo ordenado...")
    
    final_content = [preface.strip()]
    
    last_type = 'preface'
    
    for item in html_structure:
        if item['type'] == 'category':
            # Add Category Header
            # Avoid duplicate separators if sequence is Preface -> Category
            sep = "\n\n---\n\n" if last_type != 'preface' else "\n\n"
            
            cat_block = f"{sep}# 📂 SEÇÃO: {item['title']}\n\n---"
            final_content.append(cat_block)
            last_type = 'category'
            
        elif item['type'] == 'poem':
            pid = item['id']
            if pid in poem_map:
                # Add Poem
                # Ensure spacing
                p_text = poem_map[pid]
                
                # Clean up extracted block to ensure it has separators if needed, 
                # but usually we just want clean blocks separated by ---
                
                # If the block already has --- at end, remove it to normalize
                p_text = p_text.rstrip().rstrip('---').strip()
                
                sep = "\n\n---\n\n"
                # If previous was category, we still want spacing but maybe not immediate ---
                if last_type == 'category':
                    sep = "\n\n" 
                
                final_content.append(f"{sep}{p_text}")
                last_type = 'poem'
            else:
                print(f"ALERTA: Poema {pid} ainda faltando após tradução!")

    # Write to file
    with open(MARKDOWN_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_content))
    
    print("Arquivo reconstruído com sucesso!")

if __name__ == "__main__":
    main()
