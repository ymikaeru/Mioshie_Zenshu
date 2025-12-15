import json
import os
import re
import glob

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, '../Data'))
OUTPUT_FILE = os.path.join(DATA_DIR, 'advanced_search_index.json')

# Category Definitions (Keywords map to these)
CATEGORIES = {
    'health': 'Doenças e Saúde',
    'spirituality': 'Divindades e Espiritualidade',
    'johrei': 'Johrei (Purificação)',
    'society': 'Sociedade e Política',
    'art': 'Arte e Beleza',
    'agriculture': 'Agricultura',
    'religion': 'Organização Religiosa',
    'philosophy': 'Filosofia e Ensinamentos',
    'other': 'Outros'
}

# Portuguese Keywords for Classification (Lower case)
KEYWORDS = {
    'health': ['doença', 'saúde', 'medicina', 'médico', 'gripe', 'tuberculose', 'febre', 'toxina', 'vírus', 'bactéria', 'vacina', 'sangue', 'medicamento', 'hospital', 'cirurgia', 'estômago', 'rim', 'câncer', 'inflamação', 'terapia', 'farmácia'],
    'agriculture': ['agricultura', 'agrícola', 'adubo', 'colheita', 'arroz', 'trigo', 'horta', 'cultivo', 'lavoura', 'inseto', 'praga', 'sem fertilizante', 'método agrícola', 'composto'],
    'johrei': ['johrei', 'ministrar', 'outorga', 'canal', 'shoko', 'medalha', 'focalizar'],
    'art': ['arte', 'beleza', 'flor', 'belas artes', 'estética', 'poesia', 'música', 'pintura', 'museu', 'ikebana', 'cerâmica', 'tea ceremony', 'cha no yu', 'haiku', 'waka', 'tanka', 'bi no'],
    'society': ['política', 'governo', 'guerra', 'paz', 'economia', 'democracia', 'comunismo', 'lei', 'crime', 'educação', 'imposto', 'social', 'mundo', 'internacional', 'nação', 'pátria', 'juventude', 'eleição', 'partido', 'sufrágio', 'finança'],
    'religion': ['igreja', 'messiânica', 'sede', 'solo sagrado', 'membro', 'dedicação', 'culto', 'altar', 'sanguetsu', 'zuiun', 'hakone', 'khi', 'kyoshu', 'meishu-sama', 'fundador', 'oferenda'],
    'spirituality': ['deus', 'espírito', 'alma', 'milagre', 'divino', 'sagrado', 'reencarnação', 'antepassado', 'oração', 'fé', 'kannon', 'bodhisattva', 'mundo espiritual', 'espiritual', 'encosto', 'obsessão', 'encarnação', 'desencarne', 'céu', 'inferno', 'julgamento', 'satanás', 'diabo', 'anjo', 'ryujin', 'dragão'],
    'philosophy': ['verdade', 'bem', 'mal', 'felicidade', 'destino', 'amor', 'sabedoria', 'teoria', 'vontade', 'pensamento', 'razão', 'sentimento', 'homem', 'natureza humana', 'vida', 'morte', 'alegria', 'sofrimento']
}

# Folder heuristics (Code -> Category Key)
FOLDER_MAP = {
    'jorei': 'johrei',
    'no': 'agriculture',
    'ge': 'art', 
    'kouwa': 'philosophy', 
    'ke': 'health',
    'i': 'health',
    'se': 'society', # Default to society, but keyword might override to Health
    'okage': 'spirituality',
    'kikou': 'art', # Travel/Essays often artistic? Or Other.
    'situmon': 'philosophy' 
}

def classify_content(title, content, folder_code):
    """
    Classifies the item into one of the CATEGORIES based on keyword match frequency.
    Content dominating the text determines the category.
    """
    text = (title + " " + content).lower()
    
    scores = {cat: 0 for cat in CATEGORIES.values()}
    
    def COUNT(category_key, category_name):
        keywords = KEYWORDS.get(category_key, [])
        if not keywords: return
        
        # Regex to count all non-overlapping occurrences of any keyword
        # \b(k1|k2|k3)\b
        pattern = r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b'
        matches = re.findall(pattern, text)
        scores[category_name] += len(matches)

    # Calculate scores for all keyword categories
    COUNT('agriculture', CATEGORIES['agriculture'])
    COUNT('johrei', CATEGORIES['johrei'])
    COUNT('health', CATEGORIES['health'])
    COUNT('art', CATEGORIES['art'])
    COUNT('society', CATEGORIES['society'])
    COUNT('spirituality', CATEGORIES['spirituality'])
    COUNT('religion', CATEGORIES['religion'])
    COUNT('philosophy', CATEGORIES['philosophy'])
    
    # Specific disambiguation:
    # If "Spirituality" and "Religion" are close, prefer Religion terms?
    # (Already handled by counts)

    # Determine winner
    best_category = None
    max_score = 0
    
    for cat, score in scores.items():
        if score > max_score:
            max_score = score
            best_category = cat
        elif score == max_score and max_score > 0:
            # Tie breaking? 
            # Prefer Health/Johrei/Agriculture over broad Society/Philosophy?
            # For now, let's stick to first found or random. 
            # But the iteration order is arbitrary (dict).
            # Let's enforce priority if needed.
            pass
            
    if max_score > 0:
        return best_category

    # Fallback to Folder Map if no keywords matched
    if folder_code in FOLDER_MAP:
        return CATEGORIES[FOLDER_MAP[folder_code]]

    return CATEGORIES['other']

# Mapping Dictionary (Japanese/Portuguese -> Romaji)
TERM_MAPPING = {
    '栄光': 'Eikou',
    '救世': 'Kyusei',
    '光明世界': 'Koumyou Sekai',
    '地上天国': 'Chijo Tengoku',
    '東方の光': 'Touhou no Hikari',
    '明日の医術': 'Ashita no Ijutsu',
    '天国の福音': 'Tengoku no Fukuin',
    '文明の創造': 'Bunmei no Souzou',
    'Igaku Kakumei Sho': 'Igaku Kakumei no Sho',
    '全集': 'Zenshu',
    '光への道': 'Hikari e no Michi',
    '霊界叢談': 'Reikai Soudan',
    'アメリカを救う': 'America wo Sukuu',
    '観音の光': 'Kannon no Hikari',
    '日本医術講義録': 'Nihon Ijutsu Kougiroku',
    '講話': 'Kouwa',
    '御垂示': 'Gosuiji',
    '号': ' Gou',     # Issue
    '編': ' Hen',     # Volume/Part
    '書': ' Sho',     # Book
    '版': ' Ban',     # Edition
    '昭和': 'Showa ',
    '年': ' Nen',
    '月': ' Gatsu',
    '日': ' Nichi',
    '未発表': 'Mihappyou',
    '執筆': 'Shippitsu',
    '付録': 'Furoku',
    '再版': 'Saiban', # Reprint
    '初版': 'Shohan', # First edition
    '読売新聞': 'Yomiuri Shimbun',
    '岡田茂吉': 'Okada Mokichi',
    '結核問題と其解決策': 'Kekkaku Mondai to Sono Kaiketsusaku',
    '新日本医術': 'Shin Nihon Ijutsu',
    '世界救世教': 'Sekai Kyuseikyo',
    '奇蹟集': 'Kisekishu',
    '広告文': 'Kokokubun',
    '新稿': 'Shinko',
    # Portuguese Mappings
    'Ashita no Ijutsu': 'Ashita no Ijutsu',
    'Coletânea de Teses do Mestre Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Ensaios do Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'Ensaios de Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'A Questão da Tuberculose e sua Solução': 'Kekkaku Mondai to Sono Kaiketsusaku',
    'O Problema da Tuberculose e sua Solução': 'Kekkaku Mondai to Sono Kaiketsusaku',
    'Livro da Nova Arte Médica Japonesa': 'Shin Nihon Ijutsu',
    'Nova Arte Médica Japonesa': 'Shin Nihon Ijutsu',
    'Palestras de Kannon': 'Kannon Koza',
    'O Movimento de Kannon e sua Declaração': 'Kannon Undo to Sono Sengen',
    'Crônicas de uma Peregrinação Sagrada': 'Seichi Junrei Kiroku',
    'Relatos de Graças': 'Kiseki Shu',
    'Luz da Sabedoria Divina': 'Hikari no Chie',
    'Curso de Johrei': 'Jorei Koza',
    'Guia de Difusão': 'Fukyu no Tebiki',
    'Evangelho do Céu': 'Tengoku no Fukuin',
    'Criação da Civilização': 'Bunmei no Sozo',
    'Alicerce do Paraíso': 'Chijo Tengoku',
    'A Face da Verdade': 'Shinjitsu no Gao', 
    'Jornal Eikou': 'Eikou',
    'Jornal Kyusei': 'Kyusei',
    'Jornal Hikari': 'Hikari',
    'O Pão Nosso de Cada Dia': 'Hibi no Kate',
    'O que é a Medicina?': 'Igaku towa Nanizo',
    'Coleção de Teses do Mestre Okada Jikanshi': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Ensaios do Mestre Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'A Verdadeira Natureza da Tuberculose': 'Kekkaku no Shotai',
    # Ordinals / Extras
    '第一': 'Dai 1',
    '第二': 'Dai 2',
    '第三': 'Dai 3',
    '第四': 'Dai 4',
    '第五': 'Dai 5',
    '第六': 'Dai 6',
    '第七': 'Dai 7',
    '第八': 'Dai 8',
    '第九': 'Dai 9',
    '第十': 'Dai 10',
    '巻': ' Kan',
    '上': ' Jo',
    '下': ' Ge',
    '続': 'Zoku ',
    '前編': 'Zenpen',
    '後編': 'Kohen',
}

def translate_publication(text):
    if not text:
        return text
    translated = text
    # Sort keys by length descending to replace longer phrases first
    sorted_keys = sorted(TERM_MAPPING.keys(), key=len, reverse=True)
    for key in sorted_keys:
        val = TERM_MAPPING[key]
        if key in translated:
            translated = translated.replace(key, val)
    return translated

def extract_metadata(content):
    """
    Extracts Year, Publication, and Unpublished status from the content string.
    """
    metadata = {
        'year': None,
        'publication': None,
        'unpublished': False
    }

    if not content:
        return metadata

    # Check for "Unpublished" (未発表)
    if '未発表' in content[:200]: # Check start of content
        metadata['unpublished'] = True

    # Extract Year
    # Pattern 1: (1943)年
    year_match_western = re.search(r'\((\d{4})\)年', content[:200])
    if year_match_western:
        metadata['year'] = int(year_match_western.group(1))
    
    # Pattern 2: 昭和XX年 (Fallback if western year not found, or for verification)
    # Mapping Showa to Western: 1926 + Showa - 1
    if not metadata['year']:
        year_match_showa = re.search(r'昭和(\d{1,2})年', content[:200])
        if year_match_showa:
            showa_year = int(year_match_showa.group(1))
            metadata['year'] = 1925 + showa_year

    # Extract Publication
    # Pattern: 『Publication Name』
    pub_match = re.search(r'『(.*?)』', content[:200])
    if pub_match:
        # Translate to Romaji
        metadata['publication'] = translate_publication(pub_match.group(1))

    return metadata

def normalize_publication(pub_name):
    """
    Normalizes publication names to group volumes together.
    """
    if not pub_name:
        return None
    
    norm = pub_name
    # Remove "Dai X Hen", "Dai X", "Vol X"
    norm = re.sub(r'\s+Dai\s+\d+\s+Hen', '', norm, flags=re.IGNORECASE)
    norm = re.sub(r'\s+Dai\s+\d+', '', norm, flags=re.IGNORECASE)
    norm = re.sub(r'\s+Vol\.?\s*\d+', '', norm, flags=re.IGNORECASE)
    norm = re.sub(r'\s+Hen', '', norm, flags=re.IGNORECASE)
    
    # Specific cleanups
    norm = norm.replace("  ", " ").strip()
    return norm

def main():
    print("Generating Advanced Search Index...")
    all_items = []
    
    # Process all part files
    part_files = glob.glob(os.path.join(DATA_DIR, 'teachings_translated_part*.json'))
    part_files.sort()

    for part_file in part_files:
        print(f"Processing {part_file}...")
        try:
            with open(part_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for item in data:
                    # Basic info
                    entry = {
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'content_snippet': (item.get('content_ptbr') or '')[:150] + '...',
                    }

                    # Extract metadata from Japanese content header
                    extracted = extract_metadata(item.get('content', ''))
                    
                    # Classify Category
                    folder_code = item.get('category')
                    entry['category'] = classify_content(entry['title'], item.get('content_ptbr') or '', folder_code)
                    entry['tags'] = extract_tags(item.get('content_ptbr') or '')

                    entry['year'] = extracted['year']
                    entry['publication'] = extracted['publication']
                    entry['publication_group'] = normalize_publication(entry['publication'])
                    entry['unpublished'] = extracted['unpublished']
                    entry['part_file'] = os.path.basename(part_file) # Store source part file
                    
                    # Resolve URL
                    source_file = item.get('source_file')
                    if source_file:
                        # Check possible locations
                        # Note: script is in scripts/, so BASE_DIR is .../scripts
                        # We want path relative to site root (EnsinamentosAll)
                        site_root = os.path.dirname(BASE_DIR)
                        possible_prefixes = ['search1', 'search2', 'filetop']
                        found_path = None
                        
                        for prefix in possible_prefixes:
                            # Try 1: prefix/folder_code/source_file (Most likely)
                            if folder_code:
                                potential_path_sub = os.path.join(site_root, prefix, folder_code, source_file)
                                if os.path.exists(potential_path_sub):
                                    found_path = f"{prefix}/{folder_code}/{source_file}"
                                    break

                            # Try 2: prefix/source_file (Fallback)
                            potential_path_direct = os.path.join(site_root, prefix, source_file)
                            if os.path.exists(potential_path_direct):
                                found_path = f"{prefix}/{source_file}"
                                break
                        
                        if found_path:
                            entry['url'] = found_path
                        else:
                            # Fallback if not found
                            entry['url'] = source_file
                    else:
                         entry['url'] = None

                    all_items.append(entry)
                    
        except Exception as e:
            print(f"Error processing {part_file}: {e}")

    # Write output
    print(f"Calculating related articles for {len(all_items)} items...")
    
    # Create lookup map for speed
    id_map = {item['id']: item for item in all_items}
    
    # Calculate Related Articles (Simple Tag Jaccard Similarity)
    for i, item in enumerate(all_items):
        my_tags = set(item.get('tags', []))
        if not my_tags:
            continue
            
        scores = []
        for other in all_items:
            if item['id'] == other['id']:
                continue
            
            other_tags = set(other.get('tags', []))
            if not other_tags:
                continue
                
            # Jaccard Index
            intersection = len(my_tags & other_tags)
            union = len(my_tags | other_tags)
            
            if union == 0:
                score = 0
            else:
                score = intersection / union
                
            # Boost if same category
            if item.get('category') == other.get('category'):
                score += 0.1
                
            if score > 0:
                scores.append((other['id'], score))
        
        # Top 4
        scores.sort(key=lambda x: x[1], reverse=True)
        item['related'] = [s[0] for s in scores[:4]]
        
        if i % 500 == 0:
            print(f"Processed {i} relations...")

    print(f"Writing {len(all_items)} items to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print("Done.")

def extract_tags(content):
    """
    Extracts tags based on the presence of keywords in the content.
    """
    text = content.lower()
    tags = set()
    
    # Iterate through all categories and their keywords
    for cat, keywords_list in KEYWORDS.items():
        for keyword in keywords_list:
            # Simple substring match - strictly, could use regex \b boundaries
            if keyword in text:
                tags.add(keyword)
                
    return list(tags)

if __name__ == "__main__":
    main()
