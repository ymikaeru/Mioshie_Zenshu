import re
import os

markdown_path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/Data/Yama To Mizu - Tradução e Aprofundamento de Significado.md'
html_path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/gosanka/yamato.html'

# Hardcoded Preface Text (Original Japanese)
PREFACE_TEXT = """
<div align="center"><center>
<table border="0"><tr><td><p align="center">
<font face="HG正楷書体-PRO" size="1">―――　</font><font face="HG正楷書体-PRO" size="2">岡 田 自 観 師 の 御 歌 集</font><font face="HG正楷書体-PRO" size="1">　―――</font>
</p></td></tr></table>
</center></div>
<p><font size="3"><strong>　</strong></font><font face="ＭＳ 明朝" size="3"><strong>歌 集</strong></font><font face="HG正楷書体-PRO" size="5"><strong>　山 と 水</strong></font></p>

<p>はしがき</p>
<p>私は最近、古い文庫の中から見つけ出した中に、昭和六年から十年にかけて五年間に詠んだ千数百種の短歌が表われた。<br/><br/>
読んでみると、人の作品かと思わるる程に忘れている歌が大部分だ。<br/><br/>
しかしこのまま葬るには惜しい気がする。<br/><br/>
という訳で取捨選択すると共に幾分の添削もし歌集として今回出版することとなったのである。<br/><br/>
私は歌は本格的に習ったのではない。<br/><br/>
ただ好きなため､昔から今日までの本を多少読んだくらいで、まず素人歌人といってもいい。<br/><br/>
ところが万葉や古今調は、現代人にはあまりにも難解であり、といって現代調は新傾向に捉われすぎ、写実に走りすぎて品位に乏しい憾みがあると共に、言霊に於ても無関心なため、はなはだ玲瓏（れいろう）味をかいている等々で、どうも得心が出来ない。<br/><br/>
というような次第で、私は私としての個性を発揮したつもりであるから可否は読者の批判に任せるのである。<br/><br/>
昭和弐拾四年十月<br/>
熱海の寓居にて<br/>
明麿</p>
"""

def parse_markdown(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    structure = []
    
    pos = 0
    while pos < len(content):
        # Find next section or next poem
        section_match = re.search(r'# 📂 SEÇÃO:\s*(.*)', content[pos:])
        poem_match = re.search(r'##\s*(\d+)(?:\\)?\.\s*(.*?)\n', content[pos:])
        
        # Determine which comes first
        next_section_idx = section_match.start() + pos if section_match else float('inf')
        next_poem_idx = poem_match.start() + pos if poem_match else float('inf')
        
        if next_section_idx == float('inf') and next_poem_idx == float('inf'):
            break
            
        if next_section_idx < next_poem_idx:
            # Add section
            raw_title = section_match.group(1).strip()
            # Parse title: PT (JP)
            # Find last parens
            paren_match = re.search(r'(.*)\s*[(（](.*?)[)）]\s*$', raw_title)
            if paren_match:
                pt_title = paren_match.group(1).strip()
                jp_title = paren_match.group(2).strip()
            else:
                pt_title = raw_title
                jp_title = raw_title # Fallback

            structure.append({'type': 'section', 'jp_title': jp_title, 'pt_title': pt_title})
            pos = next_section_idx + len(section_match.group(0))
        else:
            # Add poem
            poem_num = poem_match.group(1)
            
            # Update pos to after header
            current_poem_start = next_poem_idx + len(poem_match.group(0))
            
            # Find boundary
            next_boundary = float('inf')
            sm = re.search(r'# 📂 SEÇÃO:', content[current_poem_start:])
            pm = re.search(r'##\s*\d', content[current_poem_start:])
            
            if sm: next_boundary = min(next_boundary, sm.start() + current_poem_start)
            if pm: next_boundary = min(next_boundary, pm.start() + current_poem_start)
            
            if next_boundary == float('inf'):
                chunk = content[current_poem_start:]
            else:
                chunk = content[current_poem_start:next_boundary]
                
            # Extract Original
            # Look for **Original:** 
            orig_match = re.search(r'\*\*Original:\*\*\s*(.*?)(?:\*\*|\n\*\*|$)', chunk, re.DOTALL)
            if orig_match:
                orig_text = orig_match.group(1).strip()
                structure.append({'type': 'poem', 'num': poem_num, 'text': orig_text})
            
            pos = next_boundary if next_boundary != float('inf') else len(content)

    return structure

def generate_jp_html(structure):
    html = []
    # Use Hardcoded Preface
    html.append(PREFACE_TEXT)
    
    html.append('<div align="center"><center><table bgcolor="#FFFFFF" border="0" width="95%" cellspacing="0" cellpadding="3">')
    
    for item in structure:
        if item['type'] == 'section':
             jp = item.get('jp_title', '')
             if not jp: jp = item.get('pt_title', '') # Fallback
             
             # Skip "Prefácio" section in table if we rendered it above?
             # But the hierarchy might expect it.
             # "Prefácio (Hashigaki)" is a section in MD.
             # If "Prefácio" matches the preface text, maybe we don't need a table header for it if no poems follow immediately?
             # For structure consistency, let's keep it but formatted nicely.
             # Actually, if the Prefácio section has NO poems (which it doesn't in MD structure, just checking MD again),
             # The first poems are in "A Primavera Passa".
             # So we can probably ignore sections that have no poems effectively?
             
             # Or just render it. A section header without poems below it is just a header.
             html.append('<tr><td colspan="3">　</td></tr>')
             html.append(f'<tr><td width="40"></td><td><font face="HG正楷書体-PRO" size="4"><strong>{jp}</strong></font></td><td></td></tr>')
        elif item['type'] == 'poem':
             html.append(f'<tr>')
             html.append(f'<td align="right" valign="top" width="40"><font color="#800000" size="2">{item["num"]}</font></td>')
             html.append(f'<td><font size="3">{item["text"]}</font></td>')
             html.append(f'<td align="center"></td>')
             html.append(f'</tr>')
             
    html.append('</table></center></div>')
    return "\n".join(html)

def update_html_file(structure):
    jp_html_content = generate_jp_html(structure)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Looking for <div id="jp-content"...> CONTENT </div><script>
    # Note: Regex might fail if nested divs are simple regex. But jp-content is likely flat except for the table I will put in.
    # The current content in the file (Step 19) looks like:
    # <div id="jp-content" ...>...</div><script>
    
    # We can search for the start tag and the next <script> tag which acts as boundary?
    # Or just search for `</div><script>` as the end of jp-content?
    
    # Pattern: (<div id="jp-content"[^>]*>)(.*?)(</div><script>)
    pattern = re.compile(r'(<div id="jp-content"[^>]*>)(.*?)(</div><script>)', re.DOTALL)
    match = pattern.search(html_content)
    
    if match:
        print(f"Found jp-content. Replacing {len(match.group(2))} chars with {len(jp_html_content)} chars.")
        new_content = match.group(1) + "\n" + jp_html_content + "\n" + match.group(3)
        final_html = html_content[:match.start()] + new_content + html_content[match.end():]
        
        with open(html_path, 'w', encoding='utf-8') as f:
             f.write(final_html)
        print("Updated yamato.html successfully.")
    else:
        print("Could not find jp-content div structure.")
        # Fallback: maybe it's just </div> without script?
        # But grep showed </div><script> in Step 19.

if __name__ == "__main__":
    if not os.path.exists(markdown_path):
        print(f"File not found: {markdown_path}")
    else:
        s = parse_markdown(markdown_path)
        print(f"Parsed {len(s)} items.")
        update_html_file(s)
