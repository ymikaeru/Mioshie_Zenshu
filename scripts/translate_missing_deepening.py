import json
import time
import os
import re
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
API_KEY = "AIzaSyDQAbBRT4SxMwdDMAwD-EGker5wp55gKNw"
SOURCE_JSON = 'gosanka/yamato_full.json'
OUTPUT_FILE = 'Data/missing_deepening.md'

# --- CONFIGURAÇÃO DA IA ---
genai.configure(api_key=API_KEY)
# Using standard Pro model for quality.
model = genai.GenerativeModel('gemini-pro-latest') 

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
"""

def load_missing_poems(path):
    print(f"Lendo dados de: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing = []
    if 'sections' not in data:
        return missing

    for section in data['sections']:
        for poem in section['poems']:
            # Check if deepening is missing or empty
            if not poem.get('deepening') or not poem.get('deepening').strip():
                try:
                    # Enrich with section title for context if needed
                    poem_data = {
                        'id': poem['number'],
                        'original': poem['original'],
                        'reading': poem['reading'],
                        'section': section['title_pt']
                    }
                    missing.append(poem_data)
                except Exception as e:
                    print(f"Skipping malformed poem: {poem} - {e}")
    
    return missing

def translate_batch(batch, attempt=1):
    prompt_content = ""
    for p in batch:
        prompt_content += f"Poema {p['id']} (Seção: {p['section']}):\nOriginal: {p['original']}\nLeitura: {p['reading']}\n\n"
    
    full_prompt = f"{PROMPT_SISTEMA}\n\n**POEMAS A TRADUZIR:**\n{prompt_content}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota" in error_str or "Resource" in error_str:
            if attempt <= 5:
                wait_time = attempt * 10 # Exponential-ish: 10, 20, 30...
                print(f"  -> Quota excedida. Aguardando {wait_time}s antes de tentar novamente (Tentativa {attempt}/5)...")
                time.sleep(wait_time)
                return translate_batch(batch, attempt + 1)
            else:
                print(f"  -> FALHA FATAL: Max retries exceeded for batch.")
                return None
        else:
            print(f"Error generating content: {e}")
            return None

def get_existing_ids(filepath):
    if not os.path.exists(filepath):
        return set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return set(int(x) for x in re.findall(r'##\s+(\d+)\.', content))

def main():
    print("--- INICIANDO TRADUÇÃO DE ITENS FALTANTES ---")
    
    poems_to_translate = load_missing_poems(SOURCE_JSON)
    existing_ids = get_existing_ids(OUTPUT_FILE)
    
    # Filter out existing
    poems_to_translate = [p for p in poems_to_translate if p['id'] not in existing_ids]
    
    print(f"Total faltando originalmente: {len(poems_to_translate) + len(existing_ids)}")
    print(f"Já traduzidos: {len(existing_ids)}")
    print(f"Restantes para traduzir: {len(poems_to_translate)}")
    
    if not poems_to_translate:
        print("Todos os poemas já foram traduzidos!")
        return

    BATCH_SIZE = 5
    successful_translations = []

    for i in range(0, len(poems_to_translate), BATCH_SIZE):
        batch = poems_to_translate[i : i+BATCH_SIZE]
        ids = [p['id'] for p in batch]
        print(f"Traduzindo batch {i//BATCH_SIZE + 1}/{(len(poems_to_translate)-1)//BATCH_SIZE + 1} -> IDs: {ids}")
        
        result_text = translate_batch(batch)
        
        if result_text:
            successful_translations.append(result_text)
            # Append immediately to file to save progress
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                f.write(result_text + "\n")
            print("  -> Salvo no arquivo.")
        else:
            print("  -> FALHA no batch.")
            
        time.sleep(2) # Avoid rate limits

    print(f"\nConcluído! Verifique o arquivo: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
