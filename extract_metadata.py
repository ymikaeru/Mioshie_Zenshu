import json
import glob
import os
import re
from bs4 import BeautifulSoup

def extract_dates():
    files = sorted(glob.glob("Data/teachings_translated_part*.json"))
    
    # Regex for Japanese dates: e.g. 昭和11(1936)年, 昭和24年, etc.
    # Matches: (EraName)(Number)(Optional Year in Parens)(Year Kanji)
    # Also handles just (1936) or pure years if needed, but usually it's Era format.
    # Improved Regex:
    # (明治|大正|昭和|平成|令和) -> Era
    # [0-9元]+ -> Year number (元 = 1)
    # (?:\(\d{4}\))? -> Optional Gregorian year in parens
    # 年 -> Kanij for Year
    
    
    # Regex for Japanese dates
    date_pattern = re.compile(r'((?:明治|大正|昭和|平成|令和)[0-9元]+(?:\(\d{4}\))?年(?:[0-9]+月(?:[0-9]+日)?)?)')
    # Also catch just Gregorian years like 1950年 if era is missing
    year_pattern = re.compile(r'(\d{4}年(?:[0-9]+月(?:[0-9]+日)?)?)')

    # Regex for Source text
    # 1. Text inside double Japanese brackets 『...』
    source_bracket_pattern = re.compile(r'『(.*?)』')
    
    # 2. Text after "資料検索 ：" (Data Search :)
    # Capture up to newline or <br> (but get_text() removes tags so just look for newline or long gaps)
    # Actually get_text() might merge lines.
    # We will look for "資料検索\s*[：:]\s*(.*)"
    # Update: Don't exclude '(', just exclude newlines. If text is huge, we'll slice it later.
    source_marker_pattern = re.compile(r'資料検索\s*[：:]\s*([^\n\r]*)')

    # Romaji Mapping Table
    romaji_map = {
        "地上天国": "Chijo Tengoku",
        "栄光": "Eikou",
        "救世": "Kyusei",
        "天国の礎": "Tengoku no Ishue",
        "道義": "Dougi",
        "御教え集": "Mioshie-shu",
        "医学革命の書": "Igaku Kakumei no Sho",
        "日本医事週報": "Nihon Iji Shuho",
        "光": "Hikari",
        "明日の医術": "Asu no Ijutsu",
        "自然農法解説": "Shizen Noho Kaisetsu",
        "結核信仰療法": "Kekkaku Shinko Ryoho",
        "アメリカ巡回": "America Junkai",
        "五六七新聞": "Miroku Shinbun",
        "健康": "Kenko",
        "文化日本": "Bunka Nihon",
        "文明の創造": "Bunmei no Sozo",
        "天国への道": "Tengoku e no Michi",
        "地上の天国が来る": "Chijo no Tengoku ga Kuru",
        "神霊と人生": "Shinrei to Jinsei",
        "世界救世道": "Sekai Kyusei Do",
        "東方の光": "Toho no Hikari",
        "信仰雑話": "Shinko Zatsuwa",
        "奇蹟物語": "Kiseki Monogatari",
        "観音講座": "Kannon Koza",
        "霊界叢談": "Reikai Sodan",
        "アメリヤ": "Ameriya",
        "祈りの栞": "Inori no Shiori",
        "御詠歌集": "Goeika-shu",
        "讃歌集": "Sanka-shu",
        "農業の大革命": "Nogyo no Daikakumei",
        "自然農法": "Shizen Noho",
        "地上天国祭": "Chijo Tengoku Sai",
        "立春祭": "Risshun Sai",
        "御光話": "Gokowa",
        "御面会": "Gomenkai",
        "御講話": "Gokowa",
        "御垂示": "Gosuiiji",
        "御論文": "Goronbun"
    }

    # Helper to convert or keep original
    def to_romaji(text):
        if not text: return ""
        # 1. Exact match
        if text in romaji_map:
            return romaji_map[text]
        # 2. Contains match (e.g. "地上天国 (8)")
        for jp, rom in romaji_map.items():
            if jp in text:
                # Replace the Japanese part with Romaji
                # e.g. "地上天国 10号" -> "Chijo Tengoku 10号"
                # But user said "no translation needed", implying strict Romaji.
                # If we can't fully convert, maybe just return the partial?
                # Let's try to replace all known terms.
                text = text.replace(jp, rom)
        
        # If text still contains Japanese specific chars, it might be unmapped.
        return text

    # Build a file map {filename: full_path} to resolve paths regardless of directory
    print("Building file map...")
    file_map = {}
    for root, dirs, files_in_dir in os.walk("."):
        for filename in files_in_dir:
            if filename.endswith(".html"):
                # Store relative path from current dir
                full_path = os.path.join(root, filename)
                # Normalize path separators
                full_path = full_path.replace("\\", "/")
                if full_path.startswith("./"):
                    full_path = full_path[2:]
                
                file_map[filename] = full_path
                
    print(f"Mapped {len(file_map)} HTML files.")

    total_updated = 0
    found_sources = set()
    
    for file_path in files:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            modified = False
            for item in data:
                source = item.get('source_file')
                if not source:
                    continue
                
                # Resolve path
                basename = os.path.basename(source)
                full_path = file_map.get(basename)
                
                if not full_path:
                    # Try direct lookup in case source has unique path not in map (unlikely if map is complete)
                    if os.path.exists(source):
                        full_path = source
                
                if not full_path or not os.path.exists(full_path):
                    # print(f"  Source not found: {source}")
                    continue
                
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as html_file:
                        content = html_file.read()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Target #jp-content text
                        jp_div = soup.find('div', id='jp-content')
                        text_to_search = ""
                        
                        if jp_div:
                            text_to_search = jp_div.get_text()
                        else:
                            # Fallback: search whole body or looking for specific text markers
                            if soup.body:
                                text_to_search = soup.body.get_text()
                        
                        # Search for date in the first chunk of text (header usually)
                        search_chunk = text_to_search[:1000] 
                        search_chunk_clean = search_chunk.replace('\n', ' ').replace('\r', ' ')

                        # --- Extract Date ---
                        found_date = None
                        
                        match_date = date_pattern.search(search_chunk)
                        
                        if match_date:
                            found_date = match_date.group(1)
                        else:
                            # Try simple year pattern
                            match_year = year_pattern.search(search_chunk)
                            if match_year:
                                found_date = match_year.group(1)
                        
                        if found_date:
                            # Clean up date string if needed
                            found_date = found_date.strip()
                            # Check if valid date string (sometimes regex captures garbage)
                            if len(found_date) < 50: 
                                item['year'] = found_date
                                # print(f"  Found date for {item.get('title')}: {found_date}")
                                modified = True

                        # --- Extract Publication Source, Title, and Status ---
                        # --- Extract Publication Source, Title, and Status ---
                        found_source = None
                        jp_title = None
                        status = None
                        
                        match_marker = source_marker_pattern.search(search_chunk_clean)
                        if match_marker:
                            # Full text after "Data Search :"
                            full_metadata = match_marker.group(1).strip()
                            
                            # 1. Extract Status
                            if "未発表" in full_metadata:
                                status = "Unpublished"
                            elif "発行" in full_metadata or "号" in full_metadata:
                                status = "Published"
                            else:
                                status = "Unknown"

                            # 2. Extract Source (Text in brackets or identified previously)
                            match_bracket = source_bracket_pattern.search(full_metadata)
                            if match_bracket:
                                found_source = match_bracket.group(1).strip()
                                # Prepare to find title: It's usually BEFORE the bracket
                                parts = full_metadata.split('『')
                                if len(parts) > 0:
                                    potential_title = parts[0].strip()
                                    if potential_title and len(potential_title) < 50:
                                         jp_title = potential_title
                            else:
                                # No brackets. Structure might be: "Title Status Date"
                                separators = [r'\s+', r'、', r',']
                                split_text = re.split('|'.join(separators), full_metadata)
                                if split_text:
                                    candidate_title = split_text[0].strip()
                                    if candidate_title and len(candidate_title) < 50:
                                        jp_title = candidate_title

                            # If source was not in brackets, use previous logic or candidates
                            if not found_source:
                                # Try to find a known source in the full string
                                for jp_src in romaji_map.keys():
                                    if jp_src in full_metadata:
                                        found_source = jp_src
                                        break
                                
                                # If still not found, fallback to the cleanup logic
                                if not found_source and jp_title:
                                     rest = full_metadata.replace(jp_title, "").strip()
                                     if rest:
                                         candidate = re.sub(r'未発表.*', '', rest).strip()
                                         candidate = re.sub(r'\d.*', '', candidate).strip() 
                                         if len(candidate) > 1:
                                             found_source = candidate

                        # --- Update JSON ---
                        if jp_title:
                            item['jp_title'] = jp_title.strip(" 、")
                            modified = True
                        
                        if status:
                            item['status'] = status
                            modified = True

                        if found_source:
                            found_source = found_source.strip()
                            if len(found_source) > 1 and len(found_source) < 100:
                                found_source = found_source.strip("、 　")
                                romaji_source = to_romaji(found_source)
                                item['publication'] = romaji_source
                                found_sources.add(found_source)
                                modified = True
                            
                except Exception as e:
                    pass 
            
            if modified:
               with open(file_path, 'w', encoding='utf-8') as f:
                   json.dump(data, f, ensure_ascii=False, indent=4)
               print(f"  Updated {file_path} with metadata.")
               total_updated += 1
                
        except Exception as e:
            print(f"Error processing JSON {file_path}: {e}")

    print(f"Done. Updated {total_updated} JSON files.")

if __name__ == "__main__":
    extract_dates()
