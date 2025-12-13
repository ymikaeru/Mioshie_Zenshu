
import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_JSON = os.path.join(BASE_DIR, 'Data', 'teachings_translated.json')
MISSING_JSON = os.path.join(BASE_DIR, 'Data', 'teachings_translated_missing.json')
BACKUP_JSON = os.path.join(BASE_DIR, 'Data', 'teachings_translated.backup.json')

def main():
    if not os.path.exists(MISSING_JSON):
        print("No missing data file found to merge.")
        return

    print("Loading datasets...")
    # Load Main
    with open(MAIN_JSON, 'r', encoding='utf-8') as f:
        main_data = json.load(f)
    print(f"Main entries: {len(main_data)}")

    # Load Missing
    with open(MISSING_JSON, 'r', encoding='utf-8') as f:
        missing_data = json.load(f)
    print(f"Missing (Recovered) entries: {len(missing_data)}")

    # Create a set of existing sources to avoid duplicates
    existing_sources = set()
    for item in main_data:
        if 'source_file' in item:
            existing_sources.add(item['source_file'])

    # Merge
    merged_count = 0
    for item in missing_data:
        if item['source_file'] not in existing_sources:
            main_data.append(item)
            merged_count += 1
    
    print(f"Merged {merged_count} new items.")

    # Backup
    if not os.path.exists(BACKUP_JSON):
        shutil.copy2(MAIN_JSON, BACKUP_JSON)
        print(f"Backup created at {BACKUP_JSON}")

    # Save
    with open(MAIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=4)
    
    print("Successfully merged and saved.")

if __name__ == "__main__":
    main()
