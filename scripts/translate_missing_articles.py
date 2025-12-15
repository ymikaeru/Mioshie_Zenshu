import json
import time
import os
import google.generativeai as genai
from google.api_core import exceptions
import concurrent.futures
import threading

# --- CONFIGURAÇÃO ---
# 1. API KEY (Do Ambiente)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERRO: A variável de ambiente GEMINI_API_KEY não está definida.")
    exit(1)

# 2. Arquivos (Caminhos Absolutos Dinâmicos)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ARQUIVO_ENTRADA = os.path.join(PROJECT_ROOT, "Data", "missing_articles.json")
ARQUIVO_SAIDA = os.path.join(PROJECT_ROOT, "Data", "missing_articles_translated.json")

# 3. Chaves do JSON
CHAVE_ID = "source_file"
CHAVE_TEXTO_JAPONES = "content_original"
CHAVE_TEXTO_PORTUGUES = "content_ptbr"

# --- CONFIGURAÇÃO DA IA ---
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

# --- PROMPT MASTER ---
PROMPT_SISTEMA = """
Atue como um tradutor editorial sênior e devoto da Sekaikyuseikyou, com vasta experiência literária nos ensinamentos de Meishu-Sama.

**Objetivo:** Traduzir o texto do japonês para o português do Brasil (PT-BR), criando um texto final que pareça ter sido originalmente escrito em português.

**Estilo e Tom (Prioridade Máxima):**
1. **Fluidez Nativa:** Abandone a sintaxe japonesa. Não traduza frase por frase isoladamente. Leia o parágrafo, entenda a ideia central e reescreva-a com a estrutura gramatical mais natural do português culto.
2. **Vocabulário Elevado:** Utilize um vocabulário rico e preciso, mantendo a dignidade de um líder religioso.

**Regras de Terminologia:**
1. **Tradução Prioritária:** Traduza todos os termos para o português sempre que houver equivalente.
2. **Exceções (Manter Japonês):** Apenas para: Nomes próprios, Locais (Shinsenkyo), e termos técnicos intraduzíveis (Kannon, yakudoku).
   - Use o formato: Termo em Romaji (Kanji Original). Ex: Kannon (観音).
3. **CRÍTICO - Títulos e Publicações:** O nome das publicações e livros NÃO devem ser traduzidos, para não perder a referência com o Japonês. Eles devem ser escritos em **Romaji**.
   - Exemplo: Não traduza 'Tijou Tengoku' como 'Paraíso Terrestre', mantenha 'Tijou Tengoku'.

**Regras de Formatação (Saída Final):**
1. Títulos originais devem ser formatados como H2 (##).
2. Não utilize negrito para enfatizar palavras dentro do corpo do texto traduzido.
3. Retorne APENAS o texto traduzido, sem comentários ou blocos de código markdown.

**Texto para tradução:**
"""

def traduzir_texto(texto_jp, titulo_ref="(Sem Título)"):
    if not texto_jp or len(texto_jp) < 2:
        return ""
    
    prompt_completo = f"{PROMPT_SISTEMA}\n\n{texto_jp}"
    max_retries = 10 
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt_completo)
            return response.text.strip()
            
        except exceptions.ResourceExhausted:
            print(f"   [!] Limite de velocidade (429). Aguardando {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        
        except Exception as e:
            erro_str = str(e)
            if "PROHIBITED_CONTENT" in erro_str or "block_reason" in erro_str:
                print(f"   [!] CONTEÚDO BLOQUEADO '{titulo_ref}': {erro_str}")
                return None
            print(f"   [!] Erro desconhecido no item '{titulo_ref}': {e}. Tentando novamente em 10s...")
            time.sleep(10)
            
    print(f"   [X] FALHA FINAL no item '{titulo_ref}' após {max_retries} tentativas.")
    return None

arquivo_lock = threading.Lock()
last_save_time = 0

def salvar_progresso(item, novos_dados):
    global last_save_time
    with arquivo_lock:
        # Check if item exists in novos_dados to avoid dupes (though logic below handles)
        # Actually list append is fine if we process by index/ID correctly
        novos_dados.append(item)
        
        now = time.time()
        if (now - last_save_time > 10) or (len(novos_dados) % 10 == 0):
            try:
                temp_file = ARQUIVO_SAIDA + ".tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(novos_dados, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp_file, ARQUIVO_SAIDA)
                last_save_time = now
            except Exception as e:
                print(f"Erro ao salvar: {e}")

def processar_item(item, total, i, mapa_traduzidos, novos_dados):
    item_id = item.get(CHAVE_ID)
    titulo = item.get('title', 'Sem Título')

    if not item_id:
        return

    if item_id in mapa_traduzidos:
         # Already translated
         return

    print(f"[{i+1}/{total}] Iniciando: {titulo} ({item_id})...")
    
    traducao = traduzir_texto(item.get(CHAVE_TEXTO_JAPONES, ""), titulo)

    if traducao:
        item[CHAVE_TEXTO_PORTUGUES] = traducao
        salvar_progresso(item, novos_dados)
        print(f"   -> [PRONTO] {titulo}")
    else:
        print(f"   -> [FALHA] {titulo}")

def main():
    print("--- INICIANDO TRADUÇÃO DE ARTIGOS FALTANTES ---")
    
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"Erro: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    novos_dados = []
    if os.path.exists(ARQUIVO_SAIDA):
        try:
            with open(ARQUIVO_SAIDA, 'r', encoding='utf-8') as f:
                novos_dados = json.load(f)
        except:
            novos_dados = []

    # Map of already translated items by ID (source_file)
    mapa_traduzidos = {item.get(CHAVE_ID): item for item in novos_dados if CHAVE_ID in item}
    
    total = len(dados)
    print(f"Total: {total} | Já traduzidos: {len(mapa_traduzidos)}")

    itens_para_processar = []
    for i, item in enumerate(dados):
        if item.get(CHAVE_ID) not in mapa_traduzidos:
             itens_para_processar.append((i, item))

    print(f"Itens restantes: {len(itens_para_processar)}")
    
    max_workers = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, item in itens_para_processar:
            future = executor.submit(processar_item, item, total, i, mapa_traduzidos, novos_dados)
            futures.append(future)
            
        for future in concurrent.futures.as_completed(futures):
            pass

    # Final Save
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        json.dump(novos_dados, f, ensure_ascii=False, indent=2)

    print(f"\n--- FIM ---")
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()
