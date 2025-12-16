
import re

def main():
    existing_ids = set()
    with open('existing_headers.txt', 'r', encoding='utf-8') as f:
        for line in f:
            # grep output format: line_num:## ID. Title
            # Regex to capture ID
            m = re.search(r'##\s*(\d+)', line)
            if m:
                existing_ids.add(int(m.group(1)))
    
    # Expected range
    all_possible = set(range(1, 1239)) # 1 to 1238
    
    missing = sorted(list(all_possible - existing_ids))
    
    print(f"Total Found: {len(existing_ids)}")
    print(f"Total Missing: {len(missing)}")
    
    if missing:
        # Group into ranges
        ranges = []
        if not missing: return
        
        start = missing[0]
        prev = missing[0]
        
        for x in missing[1:]:
            if x == prev + 1:
                prev = x
            else:
                ranges.append((start, prev))
                start = x
                prev = x
        ranges.append((start, prev))
        
        print("\nMissing Ranges:")
        for s, e in ranges:
            if s == e:
                print(f" - {s}")
            else:
                print(f" - {s} to {e} ({e-s+1} poems)")

if __name__ == "__main__":
    main()
