import re
from collections import Counter

path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all poem headers
# Matches: ## 1. Title or ## **1. Title
# Capture the number
matches = []
lines = content.split('\n')
for i, line in enumerate(lines):
    m = re.match(r'^##\s*(?:\*\*)?(\d+)', line)
    if m:
        matches.append((m.group(1), i + 1, line))

counts = Counter(m[0] for m in matches)
duplicates = [item for item, count in counts.items() if count > 1]

if duplicates:
    print(f"Found duplicate poem numbers: {duplicates}")
    for dup in duplicates:
        print(f"Locations for Poem {dup}:")
        for num, line_idx, line_content in matches:
            if num == dup:
                print(f"  Line {line_idx}: {line_content}")
else:
    print("No duplicate poem numbers found.")

# Check for duplicate sections
sections = re.findall(r'^# 📂 SEÇÃO: (.*)', content, re.MULTILINE)
section_counts = Counter(sections)
dup_sections = [item for item, count in section_counts.items() if count > 1]

if dup_sections:
    print(f"Found duplicate sections: {dup_sections}")
    # Print lines
    for dup in dup_sections:
        print(f"Locations for {dup}:")
        for i, line in enumerate(content.split('\n')):
            if f"# 📂 SEÇÃO: {dup}" in line:
                print(f"  Line {i+1}")
else:
    print("No exactly duplicate section titles found.")
