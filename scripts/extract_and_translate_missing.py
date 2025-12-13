
import os
import json
import time
import glob
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.api_core import exceptions
import concurrent.futures
import threading

# Configuration
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    # Try direct hardcoded if env var fails in this context (though it should work)
    API_KEY = "AIzaSyCod70Lx5cAH-oTHcl_Ov4wjC5cPy95VdU" 

genai.configure(api_key=API_KEY)

# Use the recovery model from the user's script
MODEL_NAME = 'gemini-2.5-pro'
model = genai.GenerativeModel(MODEL_NAME)

MISSING_FILES_LIST = "missing_files.txt"
OUTPUT_JSON = "Data/teachings_translated_missing.json" 

# --- PROMPT SYSTEM FROM translate_teachings_refined.py ---
PROMPT_SISTEMA = """
Atue como um tradutor editorial sênior e devoto da Sekaikyuseikyou, com vasta experiência literária nos ensinamentos de Meishu-Sama.

**Objetivo:** Traduzir o texto do japonês para o português do Brasil (PT-BR), criando um texto final que pareça ter sido originalmente escrito em português, e não uma tradução.

**Estilo e Tom (Prioridade Máxima):**
1. **Fluidez Nativa:** Abandone a sintaxe japonesa. Não traduza frase por frase isoladamente. Leia o parágrafo, entenda a ideia central e reescreva-a com a estrutura gramatical mais natural do português culto.
2. **Vocabulário Elevado:** Utilize um vocabulário rico e preciso (ex: prefira "estelionato" a "enganação", "reverenciar" a "respeitar"), mantendo a dignidade de um líder religioso, mas sem ser arcaico.
3. **Conexão de Ideias:** Use conectivos variados (Portanto, Contudo, Todavia, Nesse sentido) para que a leitura flua suavemente entre os parágrafos. Evite repetições excessivas de palavras como "disso", "isso" ou "aquilo".
4. **Reconstrução:** Sinta-se livre para dividir frases japonesas longas em duas ou mais frases em português para melhorar a clareza, ou unir frases curtas se isso melhorar o ritmo.

**Regras de Terminologia:**
1. **Tradução Prioritária:** Traduza todos os termos para o português sempre que houver equivalente (ex: 神 -> Deus; 霊界 -> Mundo Espiritual; 邪神 -> Espírito Maligno/Espíritos Malignos - atenção ao plural/singular pelo contexto).
2. **Exceções (Manter Japonês):** Apenas para: Nomes próprios, Locais (Shinsenkyo), e termos técnicos intraduzíveis (Kannon, yakudoku).
   - Nesses casos de exceção, use o formato: Termo em Romaji (Kanji Original). Ex: Kannon (観音).
   - Não coloque kanji para palavras traduzidas (Não use: Deus (神)).

**Regras de Formatação (Saída Final):**
1. Títulos originais devem ser formatados como H2 (##). **Traduzir TODO o título, inclusive textos entre parênteses (ex: 'Medicina do Amanhã').**
2. **Não utilize negrito** para enfatizar palavras dentro do corpo do texto traduzido.
3. Retorne APENAS o texto traduzido, sem comentários ou blocos de código markdown.

**Texto para tradução:**
"""

def traduzir_texto(texto_jp, titulo_ref="(Sem Título)"):
    if not texto_jp or len(texto_jp) < 2:
        return ""
    
    prompt_completo = f"{PROMPT_SISTEMA}\n\n{texto_jp}"
    
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt_completo)
            return response.text.strip()
            
        except exceptions.ResourceExhausted:
            print(f"   [!] Rate Limit (429) for '{titulo_ref}'. Waiting {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        
        except Exception as e:
            if "not found" in str(e):
                 # Fallback to flash if pro not found (though list_models said it is)
                 print(f"   [!] Model not found. Retrying with gemini-2.0-flash")
                 fallback_model = genai.GenerativeModel('gemini-2.0-flash')
                 try:
                     response = fallback_model.generate_content(prompt_completo)
                     return response.text.strip()
                 except:
                     pass

            print(f"   [!] Error '{titulo_ref}': {e}. Waiting 5s...")
            time.sleep(5)
            
    print(f"   [X] FAILED '{titulo_ref}' after retries.")
    return None

def parse_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Extract Title
        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)
        
        body_title = soup.find('font', {'size': '5'})
        if body_title:
            title = body_title.get_text(strip=True)

        body = soup.body
        if not body:
            return None

        for s in body(['script', 'style']):
            s.decompose()

        text_content = body.get_text(separator='\n', strip=True)
        
        return {
            "title": title,
            "content_jp": text_content,
            "source_file": file_path
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

# Thread safe list
translated_data = []
data_lock = threading.Lock()

def process_file(file_path):
    parsed = parse_html_file(file_path)
    if not parsed:
        return

    # Check content length - if too short, might be just nav
    if len(parsed['content_jp']) < 10:
        return

    basename = os.path.basename(file_path)
    
    # Translate
    content_pt = traduzir_texto(parsed['content_jp'], basename)
    
    if content_pt:
        item = {
            "title": parsed['title'], 
            "content_ptbr": content_pt,
            "content_jp": parsed['content_jp'],
            "source_file": file_path,
            "category": "missing_recovered"
        }
        
        with data_lock:
            translated_data.append(item)
            if len(translated_data) % 5 == 0:
                print(f"   -> Progress: {len(translated_data)} items translated.")
                save_temp()

def save_temp():
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=4)

def main():
    if not os.path.exists(MISSING_FILES_LIST):
        print("missing_files.txt not found.")
        return

    with open(MISSING_FILES_LIST, 'r') as f:
        files = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(files)} files with {MODEL_NAME}...")
    
    # Load existing to resume
    global translated_data
    if os.path.exists(OUTPUT_JSON):
        try:
             with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                translated_data = json.load(f)
        except:
             pass
             
    processed_paths = {item['source_file'] for item in translated_data}
    remaining_files = [f for f in files if f not in processed_paths]
    
    print(f"Remaining to process: {len(remaining_files)}")

    # Use ThreadPool
    MAX_WORKERS = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, f): f for f in remaining_files}
        
        for future in concurrent.futures.as_completed(futures):
            pass # exceptions logged in process_file

    save_temp()
    print("Done.")

if __name__ == "__main__":
    main()
