
import re

text = "―― 岡田自観師の論文集 ―― 御教え検索 ： help 資料検索 ： 西洋医学の野蛮性 『明日の医術 第二編』昭和18(1943)年10月5日発行 昭和十七年六月三十日付の手紙が..."
search_chunk_clean = text # mocking the cleaned chunk

# Current Regex
source_marker_pattern_old = re.compile(r'資料検索\s*[：:]\s*([^(\n\r]*)')
match_old = source_marker_pattern_old.search(search_chunk_clean)

print("--- OLD REGEX ---")
if match_old:
    print(f"Captured: '{match_old.group(1)}'")
else:
    print("No match")

# Proposed Regex (simple relaxation)
# Remove ( from exclusion
source_marker_pattern_new = re.compile(r'資料検索\s*[：:]\s*([^\n\r]*)') 
# Since input has no newlines, this matches to end of string. 
# We might want to limit it or matching logic handles it.
match_new = source_marker_pattern_new.search(search_chunk_clean)

print("\n--- NEW REGEX (No exclusion) ---")
if match_new:
    captured = match_new.group(1)
    # Simulate truncation to reasonable length if it captures too much (e.g. 200 chars)
    captured = captured[:200]
    print(f"Captured: '{captured}'")
    
    status = "Unknown"
    if "未発表" in captured:
        status = "Unpublished"
    elif "発行" in captured or "号" in captured:
        status = "Published"
    print(f"Status: {status}")
else:
    print("No match")
