#!/usr/bin/env python3
"""
Script to re-extract missing "meaning" content from markdown source
"""

import json
import re

# Read the markdown source
print("Reading markdown source...")
with open('Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Read the current poems.json
print("Reading poems.json...")
with open('Data/poems.json', 'r', encoding='utf-8') as f:
    poems = json.load(f)

# Build a dictionary of missing poems by title
missing_titles = set()
for poem in poems:
    meaning = poem.get('meaning', '')
    if not meaning or meaning.strip() == '':
        title = poem.get('title', '')
        if title:
            missing_titles.add(title)

print(f"Missing poems to search: {len(missing_titles)}")

# Parse markdown by splitting into sections
sections = re.split(r'\n---\n', md_content)

extracted = {}
for section in sections:
    # Find title line (## NUMBER. TITLE)
    title_match = re.search(r'##\s*\d+\.?\s*([^\n]+)', section)
    if not title_match:
        continue
    
    title = title_match.group(1).strip()
    
    # Look for lesson/deepening content
    # Patterns: **🏔️ Lição:** or **🏔️ A Profundidade (Lição Espiritual):**
    lesson_match = re.search(
        r'(?:\*\*🏔️[^:]*:\*\*|🏔️[^\n]*:)\s*(.+?)(?:\n\n|\Z)',
        section,
        re.DOTALL
    )
    
    if lesson_match:
        content = lesson_match.group(1).strip()
        # Clean up
        content = re.sub(r'\s+', ' ', content)
        if len(content) > 20:
            extracted[title] = content

print(f"Extracted poems from markdown: {len(extracted)}")

# Match and update
updated = 0
for poem in poems:
    title = poem.get('title', '')
    meaning = poem.get('meaning', '')
    
    if (not meaning or meaning.strip() == '') and title in extracted:
        poem['meaning'] = extracted[title]
        updated += 1
        print(f"✓ Updated: {title}")

print(f"\nTotal updated: {updated}/{len(missing_titles)}")

# Save
with open('Data/poems.json', 'w', encoding='utf-8') as f:
    json.dump(poems, f, ensure_ascii=False, indent=4)

print("Saved poems.json")
