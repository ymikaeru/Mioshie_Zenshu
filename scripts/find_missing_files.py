import os
import json
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(BASE_DIR, 'Data', 'teachings_manifest.json')
DATA_DIR = os.path.join(BASE_DIR, 'Data')

def load_all_translations(manifest_path):
    print(f"Loading manifest from {manifest_path}...")
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"Error: Manifest file {manifest_path} not found.")
        return []
    
    all_translations = []
    for filename in manifest.get('files', []):
        part_path = os.path.join(DATA_DIR, filename)
        print(f"Loading {part_path}...")
        try:
            with open(part_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_translations.extend(data)
                else:
                    print(f"Warning: {filename} does not contain a list.")
        except FileNotFoundError:
            print(f"Error: File {part_path} not found.")
            
    return all_translations

def find_missing_files(manifest_path, base_dir):
    # Load all translations
    data = load_all_translations(manifest_path)
    
    if not data:
        print("No translation data loaded.")
        return

    # Create a set of basenames from the JSON 'source_file' field
    existing_files = set()
    for item in data:
        if 'source_file' in item and item['source_file']:
            existing_files.add(os.path.basename(item['source_file']).strip())

    print(f"Loaded {len(existing_files)} unique source files from {len(data)} translation entries.")

    # Find all HTML files in base_dir
    search_pattern = os.path.join(base_dir, '**', '*.html')
    all_html_files = glob.glob(search_pattern, recursive=True)

    missing_files = []
    
    # Exclude common non-content files
    excludes = ['index.html', 'readme.html', 'readme1.html', '2.html', '3.html', 'koshin.html', 'koshin1.html', 'koshin2.html', 'yogosyu0.html']
    # Also exclude generated index files
    exclude_prefixes = ['idx_pt_']

    for file_path in all_html_files:
        basename = os.path.basename(file_path)
        
        if basename in excludes:
            continue
            
        if any(basename.startswith(prefix) for prefix in exclude_prefixes):
            continue
            
        if basename not in existing_files:
            missing_files.append(file_path)

    print(f"Found {len(missing_files)} HTML files not present in translations.")
    
    # Save list to file for inspection
    with open('missing_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"Analysis Report\n")
        f.write(f"Total Translation Entries: {len(data)}\n")
        f.write(f"Unique Referenced Files: {len(existing_files)}\n")
        f.write(f"Total HTML Files Found on Disk: {len(all_html_files)}\n")
        f.write(f"Files on Disk NOT in Translations: {len(missing_files)}\n")
        f.write("-" * 50 + "\n")
        for mf in missing_files:
            f.write(mf + '\n')
            
    print("Report saved to missing_report.txt")

if __name__ == "__main__":
    find_missing_files(MANIFEST_PATH, BASE_DIR)
