import json
import glob
import os

MAX_CHARS_PER_FILE = 500000  # ~500KB per file

def write_chunked(articles, base_name, output_dir="Markdown"):
    """
    Writes articles to multiple markdown files, ensuring no file exceeds MAX_CHARS_PER_FILE.
    articles: List of dicts {title, content_block}
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    part_num = 1
    current_chars = 0
    current_lines = []
    
    total_files = 0
    
    # Header for the first part
    current_lines.append(f"# {base_name} - Part {part_num}\n\n")

    for article in articles:
        text = article['content_block']
        
        # If adding this article exceeds limit (and we have content), write current batch
        if current_chars + len(text) > MAX_CHARS_PER_FILE and current_lines:
            # Write current file
            filename = f"{base_name}_Part_{part_num:02d}.md"
            path = os.path.join(output_dir, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(current_lines)
            print(f"  -> Created {path} ({current_chars} chars)")
            total_files += 1
            
            # Reset for next part
            part_num += 1
            current_lines = []
            current_chars = 0
            current_lines.append(f"# {base_name} - Part {part_num}\n\n")
        
        current_lines.append(text)
        current_lines.append("\n---\n\n")
        current_chars += len(text)

    # Write remaining content
    if current_lines:
        filename = f"{base_name}_Part_{part_num:02d}.md"
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(current_lines)
        print(f"  -> Created {path} ({current_chars} chars)")
        total_files += 1

    return total_files

def export_teachings():
    print("--- Exporting Teachings from JSON ---")
    files = sorted(glob.glob("Data/teachings_translated_part*.json"))
    
    all_articles = []
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                title = item.get('title', 'Sem Título')
                content = item.get('content_ptbr', '')
                category = item.get('category', 'Geral')
                year = item.get('year', '-')
                publication = item.get('publication', '-')
                
                if not content:
                    continue
                
                # Format the article block
                block = f"# {title}\n\n"
                block += f"**Categoria:** {category} | **Ano:** {year} | **Fonte:** {publication}\n\n"
                block += f"{content}\n"
                
                all_articles.append({
                    'title': title,
                    'content_block': block
                })
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"Total articles found: {len(all_articles)}")
    write_chunked(all_articles, "Mioshie_Teachings")

def export_yamatomizu():
    print("\n--- Exporting Yama To Mizu ---")
    input_path = "Markdown/ForBotebookLM.md"
    if not os.path.exists(input_path):
        # Fallback to Data dir if not found (though previous steps renamed it)
        input_path = "Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md"
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Parse into "blocks" (Poems) based on Headers
        blocks = []
        current_block = []
        
        for line in lines:
            # New block starts at # SEÇÃO or ## Number
            if line.strip().startswith("# ") or line.strip().startswith("## "):
                if current_block:
                    blocks.append({'content_block': "".join(current_block)})
                    current_block = []
            current_block.append(line)
            
        if current_block:
            blocks.append({'content_block': "".join(current_block)})

        print(f"Total blocks (sections/poems) found: {len(blocks)}")
        write_chunked(blocks, "YamaToMizu")
        
    except Exception as e:
        print(f"Error processing YamaToMizu: {e}")

def export_teachings_jp():
    print("\n--- Exporting Teachings (Japanese) from JSON ---")
    files = sorted(glob.glob("Data/teachings_translated_part*.json"))
    
    all_articles = []
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                title = item.get('title', '無題')
                # Use 'content' for Japanese text
                content = item.get('content', '')
                category = item.get('category', 'Geral')
                year = item.get('year', '-')
                publication = item.get('publication', '-')
                
                if not content:
                    continue
                
                # Format the article block
                block = f"# {title} ({item.get('id', '')})\n\n"
                block += f"**Category:** {category} | **Year:** {year} | **Source:** {publication}\n\n"
                block += f"{content}\n"
                
                all_articles.append({
                    'title': title,
                    'content_block': block
                })
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"Total JP articles found: {len(all_articles)}")
    write_chunked(all_articles, "Mioshie_Teachings_JP")

def export_yamatomizu_jp():
    print("\n--- Exporting Yama To Mizu (Japanese) ---")
    
    # Read from the split parts we just generated/have
    input_files = sorted(glob.glob("Markdown/YamaToMizu_Part_*.md"))
    
    if not input_files:
        # Fallback to older paths if split files don't exist yet/deleted?
        # But we expect them to exist from export_yamatomizu() run.
        possible_paths = [
            "Markdown/ForBotebookLM.md", 
            "Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                input_files = [p]
                break
    
    if not input_files:
        print("No source files found for YamaToMizu JP export.")
        return

    blocks = []
    import re
    
    current_title = ""
    
    for file_path in input_files:
        print(f"Reading {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line.startswith("## "):
                    current_title = re.sub(r'^\d+\.\s*', '', line.replace("## ", "")) # Clean numbering "1. Title" -> "Title"
                
                if "**Original:**" in line:
                    match = re.search(r'\*\*Original:\*\*(.*?)(?:\*\*Leitura:|$)', line)
                    if match:
                        jp_text = match.group(1).strip()
                        if jp_text:
                            # Add Numbering/ID if possible, or just Title
                            block = f"## {current_title}\n\n{jp_text}\n"
                            blocks.append({'content_block': block})
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    print(f"Total JP poems found: {len(blocks)}")
    write_chunked(blocks, "YamaToMizu_JP")

if __name__ == "__main__":
    export_teachings()
    export_yamatomizu()
    export_teachings_jp()
    export_yamatomizu_jp()
