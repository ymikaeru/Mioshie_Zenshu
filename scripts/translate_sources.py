
import os
import re
from bs4 import BeautifulSoup

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories containing files to update (Update ALL content directories)
INDEX_DIRS = [
    os.path.join(BASE_DIR, 'filetop'),
    os.path.join(BASE_DIR, 'hakkousi'),
    os.path.join(BASE_DIR, 'kanren'),
    os.path.join(BASE_DIR, 'search1'),
    os.path.join(BASE_DIR, 'search2'),
    os.path.join(BASE_DIR, 'search3'),
    os.path.join(BASE_DIR, 'search4'),
    os.path.join(BASE_DIR, 'search5'),
    os.path.join(BASE_DIR, 'search6'),
    os.path.join(BASE_DIR, 'search7'),
    os.path.join(BASE_DIR, 'search8'),
    os.path.join(BASE_DIR, 'search9'),
    os.path.join(BASE_DIR, 'search10'),
    os.path.join(BASE_DIR, 'search11'),
    os.path.join(BASE_DIR, 'search12'),
    os.path.join(BASE_DIR, 'miosie'),
]

# Mapping Dictionary
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
}

def translate_text(text):
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

def main():
    print("Starting source name translation...")
    
    for index_dir in INDEX_DIRS:
        if not os.path.exists(index_dir):
            continue
            
        print(f"Scanning directory: {index_dir}")
        for root, dirs, files in os.walk(index_dir):
            for filename in files:
                if not filename.endswith('.html'):
                    continue
                    
                file_path = os.path.join(root, filename)
                updated = False
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        soup = BeautifulSoup(f, 'html.parser')
                    
                    # Find the main data table
                    tables = soup.find_all('table')
                    for table in tables:
                        rows = table.find_all('tr')
                        if len(rows) < 2:
                            continue
                        
                        # Process data rows
                        for row in rows[1:]:
                            cells = row.find_all('td')
                            for cell in cells:
                                for string in cell.strings:
                                    if string.strip():
                                        new_text = translate_text(string)
                                        if new_text != string:
                                            string.replace_with(new_text)
                                            updated = True

                    if updated:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"Updated {filename}")
                        
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    print("Source translation complete.")

if __name__ == "__main__":
    main()
