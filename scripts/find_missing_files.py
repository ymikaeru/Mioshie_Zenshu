
import os
import json
import glob

def find_missing_files(json_path, base_dir):
    # Load existing JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found.")
        return

    # Create a set of basenames from the JSON 'source_file' field
    # We strip whitespace just in case
    existing_files = set()
    for item in data:
        if 'source_file' in item and item['source_file']:
            existing_files.add(os.path.basename(item['source_file']).strip())

    print(f"Loaded {len(existing_files)} entries from JSON.")

    # Find all HTML files in base_dir
    # we look for .html in current and subfolders (recursive might be needed depending on structure)
    # The user's htmls seem to be in subfolders like 'miosie', 'sashi', etc.
    # We'll use glob recursive
    search_pattern = os.path.join(base_dir, '**', '*.html')
    all_html_files = glob.glob(search_pattern, recursive=True)

    missing_files = []
    
    # Exclude common non-content files
    excludes = ['index.html', 'readme.html', 'readme1.html', '2.html', '3.html', 'koshin.html', 'koshin1.html', 'koshin2.html', 'yogosyu0.html']

    for file_path in all_html_files:
        basename = os.path.basename(file_path)
        
        if basename in excludes:
            continue
            
        # Basic check to skip tiny files if necessary, or just rely on name
        # But let's rely on name for now.
        
        if basename not in existing_files:
            missing_files.append(file_path)

    print(f"Found {len(missing_files)} missing HTML files.")
    
    # Save list to file for inspection
    with open('missing_files.txt', 'w', encoding='utf-8') as f:
        for mf in missing_files:
            f.write(mf + '\n')
            
    print("List saved to missing_files.txt")

if __name__ == "__main__":
    BASE_DIR = os.getcwd() # Should be /Users/michael/Documents/Ensinamentos/EnsinamentosAll
    JSON_PATH = os.path.join(BASE_DIR, 'Data', 'teachings_translated.json')
    find_missing_files(JSON_PATH, BASE_DIR)
