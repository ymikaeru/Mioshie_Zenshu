import re

path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all poem numbers
matches = re.findall(r'^##\s*(?:\*\*)?(\d+)', content, re.MULTILINE)
numbers = [int(n) for n in matches]
numbers.sort()

print(f"Total poems found: {len(numbers)}")
if numbers:
    print(f"Range: {numbers[0]} to {numbers[-1]}")

    # Check for gaps
    missing = []
    for i in range(numbers[0], numbers[-1] + 1):
        if i not in numbers:
            missing.append(i)
    
    if missing:
        print(f"Missing poem numbers ({len(missing)}): {missing}")
    else:
        print("No missing poem numbers in the sequence.")

    # Check for duplicates again (just in case)
    from collections import Counter
    counts = Counter(numbers)
    dups = [n for n, c in counts.items() if c > 1]
    if dups:
        print(f"Duplicates remaining: {dups}")
else:
    print("No poems found.")
