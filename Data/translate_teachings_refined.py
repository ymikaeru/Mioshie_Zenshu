import json
import time
import os
import google.generativeai as genai
from google.api_core import exceptions

# --- CONFIGURAÇÃO ---
# 1. API KEY (Do Ambiente)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERRO: A variável de ambiente GEMINI_API_KEY não está definida.")
    print("Execute: export GEMINI_API_KEY='sua_chave_aqui'")
    exit(1)

# 2. Arquivos (Caminhos Absolutos Dinâmicos)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ARQUIVO_ENTRADA = os.path.join(PROJECT_ROOT, "data", "teachings.json")
ARQUIVO_SAIDA = os.path.join(PROJECT_ROOT, "data", "teachings_translated.json")

# 3. Chaves do JSON
CHAVE_TEXTO_JAPONES = "content"
CHAVE_TEXTO_PORTUGUES = "content_ptbr"

# --- CONFIGURAÇÃO DA IA ---
genai.configure(api_key=API_KEY)
# Usando gemini-2.5-pro (Qualidade Máxima - Fila de Espera)
model = genai.GenerativeModel('gemini-2.5-pro')

# --- PROMPT MASTER (Do Usuário) + REGRAS DE ESTRUTURA ---
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
    
    # Prompt montado com o texto
    prompt_completo = f"{PROMPT_SISTEMA}\n\n{texto_jp}"
    
    max_retries = 10 
    retry_delay = 5 # Começa rápido

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt_completo)
            return response.text.strip()
            
        except exceptions.ResourceExhausted:
            # Erro 429: Rate Limit
            print(f"   [!] Limite de velocidade (429). Aguardando {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60) # Backoff exponencial até 60s
        
        except Exception as e:
            # Tentar identificar bloqueios
            erro_str = str(e)
            if "PROHIBITED_CONTENT" in erro_str or "block_reason" in erro_str:
                print(f"   [!] CONTEÚDO BLOQUEADO '{titulo_ref}': {erro_str}")
                # Logar em arquivo separado imediatamente
                log_blocked_item(titulo_ref, texto_jp, erro_str)
                return None # Não tenta novamente se foi bloqueado por segurança

            print(f"   [!] Erro desconhecido no item '{titulo_ref}': {e}. Tentando novamente em 10s...")
            time.sleep(10)
            
    print(f"   [X] FALHA FINAL no item '{titulo_ref}' após {max_retries} tentativas.")
    return None

def log_blocked_item(titulo, conteudo_original, erro):
    blocked_file = os.path.join(PROJECT_ROOT, "data", "blocked_items.json")
    
    entry = {
        "title": titulo,
        "error": erro,
        "original_content": conteudo_original,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Append seguro com lock (usando o mesmo lock ou um novo, mas append em arquivo é atômico em OSes modernos em append mode, mas JSON precisa de read/write)
    # Vamos usar um arquivo JSONL (JSON Lines) para ser mais fácil de dar append sem ler tudo
    with open(blocked_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

import concurrent.futures
import threading

# ... (Previous imports and config remain same)

# Lock para escrita no arquivo
arquivo_lock = threading.Lock()
last_save_time = 0

def salvar_progresso(item, novos_dados):
    global last_save_time
    # Adicionar à lista em memória é rápido e seguro com lock
    with arquivo_lock:
        novos_dados.append(item)
        
        # Debounce: Salvar apenas a cada 5 segundos ou a cada 10 itens?
        # Vamos usar tempo.
        import time
        now = time.time()
        
        # Salva se passou 10 segundos desde o último save OU se a lista for múltipla de 20 (para garantir periodicidade por volume)
        if (now - last_save_time > 10) or (len(novos_dados) % 20 == 0):
            try:
                temp_file = ARQUIVO_SAIDA + ".tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(novos_dados, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno()) # Garante que foi p disco
                
                os.replace(temp_file, ARQUIVO_SAIDA) # Atomic move
                last_save_time = now
            except Exception as e:
                print(f"Erro ao salvar: {e}")

def processar_item(item, total, i, mapa_traduzidos, novos_dados):
    item_id = item.get('id')
    titulo = item.get('title', 'Sem Título')

    if not item_id:
        return

    # Check rápido (sem lock pois leitura de mapa estático)
    if item_id in mapa_traduzidos and mapa_traduzidos[item_id].get(CHAVE_TEXTO_PORTUGUES):
        return

    print(f"[{i+1}/{total}] Iniciando: {titulo}...")
    
    traducao = traduzir_texto(item.get(CHAVE_TEXTO_JAPONES, ""), titulo)

    if traducao:
        # Extrair título traduzido se disponível (## Titulo)
        lines = traducao.split('\n')
        if lines and lines[0].strip().startswith('##'):
            novo_titulo = lines[0].strip().replace('#', '').strip()
            if novo_titulo:
                item['title'] = novo_titulo # Atualiza o título no objeto JSON
        
        item[CHAVE_TEXTO_PORTUGUES] = traducao
        # Seção crítica: Salvar
        salvar_progresso(item, novos_dados)
        print(f"   -> [PRONTO] {titulo}")
    else:
        print(f"   -> [FALHA] {titulo}")

def main():
    print("--- INICIANDO TRADUÇÃO (MODO TURBO: 5x THREADS) ---")
    print(f"Modelo: gemini-2.5-pro")
    
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"Erro: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Carregar progresso
    novos_dados = []
    if os.path.exists(ARQUIVO_SAIDA):
        try:
            with open(ARQUIVO_SAIDA, 'r', encoding='utf-8') as f:
                novos_dados = json.load(f)
        except:
            novos_dados = []

    mapa_traduzidos = {item.get('id'): item for item in novos_dados if 'id' in item}
    
    total = len(dados)
    print(f"Total: {total} | Já traduzidos: {len(mapa_traduzidos)}")

    # Fila de trabalho
    itens_para_processar = []
    for i, item in enumerate(dados):
        if item.get('id') not in mapa_traduzidos:
             itens_para_processar.append((i, item))

    print(f"Itens restantes: {len(itens_para_processar)}")
    
    # Execução Serial (Qualidade Máxima - Paciência)
    # 1 thread para aguardar o fim do rate limit sem sacrificar qualidade.
    # Reduzindo para 5 threads para evitar Rate Limit excessivo (429)
    max_workers = 5
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, item in itens_para_processar:
            # Envia para o pool
            future = executor.submit(processar_item, item, total, i, mapa_traduzidos, novos_dados)
            futures.append(future)
            
        # Aguarda conclusão
        for future in concurrent.futures.as_completed(futures):
            pass

    print(f"\n--- FIM (TURBO) ---")
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()
