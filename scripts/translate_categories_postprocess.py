
import re
import google.generativeai as genai
import os

API_KEY = "AIzaSyC3e_S5y_ZOAMn_qyqxFoCEmD1TPR-RxUU"
MARKDOWN_FILE = 'Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

def translate_titles(titles):
    prompt = """
    Traduza os seguintes títulos de seções de um livro de poesia (Waka) do Japonês para o Português.
    Mantenha o estilo poético e curto.
    Retorne APENAS o JSON no formato: {"Original": "Tradução"}
    
    Títulos:
    """ + "\n".join(titles)
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean markdown code blocks if present
        text = text.replace('```json', '').replace('```', '')
        return eval(text) # unsafe but quick for this context
    except Exception as e:
        print(f"Translation Error: {e}")
        return {}

def main():
    if not os.path.exists(MARKDOWN_FILE):
        print("Arquivo não encontrado.")
        return

    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all headers: # 📂 SEÇÃO: [Japanese Title]
    # Regex to capture the title
    matches = re.findall(r'# 📂 SEÇÃO: (.+)', content)
    unique_titles = list(set(matches))
    
    # Filter only Japanese ones (heuristic: contains non-ascii)
    jp_titles = [t for t in unique_titles if not all(ord(c) < 128 for c in t)]
    
    print(f"Found {len(jp_titles)} Japanese category headers.")
    
    if not jp_titles:
        print("No Japanese headers to translate.")
        return

    translations = translate_titles(jp_titles)
    
    new_content = content
    for original, translated in translations.items():
        # Replace "# 📂 SEÇÃO: Original" with "# 📂 SEÇÃO: Translated (Original)"
        pattern = f"# 📂 SEÇÃO: {re.escape(original)}"
        replacement = f"# 📂 SEÇÃO: {translated} ({original})"
        new_content = re.sub(pattern, replacement, new_content)
        print(f"Updated: {original} -> {translated}")

    with open(MARKDOWN_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Done updating headers.")

if __name__ == "__main__":
    main()
