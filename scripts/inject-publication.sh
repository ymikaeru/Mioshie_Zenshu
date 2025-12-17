#!/bin/bash
# Inject publication-global.js into all HTML files

BASE_DIR="/Users/michael/Documents/Ensinamentos/Mioshie_Zenshu"
SCRIPT_TAG='<script src="../../scripts/publication-global.js"></script>'

# Exclude certain files
EXCLUDE_PATTERN="login.html|publicacao.html|advanced_search.html|index.html|timeline.html"

# Find all HTML files
find "$BASE_DIR" -name "*.html" -type f | while read file; do
    # Skip excluded files
    if echo "$file" | grep -qE "$EXCLUDE_PATTERN"; then
        continue
    fi
    
    # Skip if already has publication-global.js
    if grep -q "publication-global.js" "$file"; then
        continue
    fi
    
    # Calculate relative path to scripts folder
    rel_path=$(python3 -c "import os.path; print(os.path.relpath('$BASE_DIR/scripts/', os.path.dirname('$file')))")
    
    # Create the script tag with correct path
    script_tag="<script src=\"${rel_path}/publication-global.js\"></script>"
    
    # Inject before </body>
    if grep -q "</body>" "$file"; then
        sed -i '' "s|</body>|${script_tag}</body>|" "$file"
        echo "Injected: $file"
    fi
done

echo "Done!"
