
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILE = os.path.join(BASE_DIR, 'filetop', 'itiran.html')

TERM_MAPPING = {
    # Japanese to Romaji
    '栄光': 'Eikou',
    '救世': 'Kyusei',
    '光明世界': 'Koumyou Sekai',
    '地上天国': 'Chijo Tengoku',
    '東方の光': 'Touhou no Hikari',
    '明日の医術': 'Ashita no Ijutsu',
    '天国の福音': 'Tengoku no Fukuin',
    '文明の創造': 'Bunmei no Souzou',
    '全集': 'Zenshu',
    '光への道': 'Hikari e no Michi',
    '霊界叢談': 'Reikai Soudan',
    'アメリカを救う': 'America wo Sukuu',
    '観音の光': 'Kannon no Hikari',
    '日本医術講義録': 'Nihon Ijutsu Kougiroku',
    '講話': 'Kouwa',
    '御垂示': 'Gosuiji',
    '結核問題と其解決策': 'Kekkaku Mondai to Sono Kaiketsusaku',
    '新日本医術': 'Shin Nihon Ijutsu',
    '世界救世教': 'Sekai Kyuseikyo',
    '奇蹟集': 'Kisekishu',
    '結核の正体': 'Kekkaku no Shotai',
    '結核信仰療法': 'Kekkaku Shinko Ryoho',
    '結核の革命的療法': 'Kekkaku no Kakumeiteki Ryoho',
    '自然農法解説': 'Shizen Noho Kaisetsu',
    '一信者の告白': 'Ichi Shinja no Kokuhaku',
    '新しき暴力': 'Atarashiki Boryoku',
    '自観叢書': 'Jikan Sosho',
    '讃歌集': 'Sanka Shu',
    '山と水': 'Yama to Mizu',
    '法難手記': 'Honan Shuki',
    '教えの光': 'Oshie no Hikari',
    '御教え集': 'Mioshie Shu',
    '御光話録': 'Gokowa Roku',
    '御面会記録': 'Gomenkai Kiroku',
    '機関誌': 'Kikanshi',
    '絵葉書': 'Ehagaki',
    
    # Portuguese to Romaji
    'Coletânea de Teses do Mestre Okada Jikanshi': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Teses do Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'Coleção de Teses do Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Teses do Mestre Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'Coleção de Teses do Mestre Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Ensaios do Mestre Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Ensaios do Reverendo Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'Coletânea de Ensaios do Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'Coleção de Ensaios do Mestre Okada Jikan': 'Okada Jikan Shi Ronbunshu',
    'Coleção de Ensaios do Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu',
    'Okada Jikan Shi Ronbunshushi': 'Okada Jikan Shi Ronbunshu',
    'Ensaios de Mestre Jikan Okada': 'Okada Jikan Shi Ronbunshu', 
    'A Questão da Tuberculose e sua Solução': 'Kekkaku Mondai to Sono Kaiketsusaku',
    'O Problema da Tuberculose e sua Solução': 'Kekkaku Mondai to Sono Kaiketsusaku',
    'Livro da Nova Arte Médica Japonesa': 'Shin Nihon Ijutsu',
    'Nova Arte Médica Japonesa': 'Shin Nihon Ijutsu',
    'Palestras de Kannon': 'Kannon Koza',
    'O Movimento de Kannon e sua Declaração': 'Kannon Undo to Sono Sengen',
    'Crônicas de uma Peregrinação Sagrada': 'Seichi Junrei Kiroku',
    'Relatos de Graças': 'Kiseki Shu',
    'Relatos de Milagres': 'Kiseki Shu',
    'Luz da Sabedoria Divina': 'Hikari no Chie',
    'Curso de Johrei': 'Jorei Koza',
    'Guia de Difusão': 'Fukyu no Tebiki',
    'Evangelho do Céu': 'Tengoku no Fukuin',
    'Criação da Civilização': 'Bunmei no Sozo',
    'Alicerce do Paraíso': 'Chijo Tengoku',
    'Paraíso Terrestre': 'Chijo Tengoku',
    'A Face da Verdade': 'Shinjitsu no Gao',
    'Jornal Eikou': 'Eikou',
    'Jornal Kyusei': 'Kyusei',
    'Jornal Hikari': 'Hikari',
    'O Pão Nosso de Cada Dia': 'Hibi no Kate',
    'O que é a Medicina?': 'Igaku towa Nanizo',
    'A Verdadeira Natureza da Tuberculose': 'Kekkaku no Shotai',
    'Salvar a América': 'America wo Sukuu',
    'A Salvação da América': 'America wo Sukuu',
    'Registro da Perseguição Religiosa': 'Honan Shuki',
    'Um Guia Rápido sobre a Sekaikyuseikyou': 'Sekai Kyuseikyo Hayawakari',
    'Breve Elucidação sobre a Arte Médica do Johrei': 'Jorei Ijutsu no Kan-i',
    'O Desígnio da Criação do Museu de Arte': 'Bijutsukan Kensetsu no Ito',
    'UMA HISTÓRIA DO UKIYO-E': 'Ukiyo-e no Hanashi',
    'Postais de Shinsenkyo': 'Shinsenkyo Ehagaki',
    '箱根美術館': 'Hakone Bijutsukan',
    '熱海地上天国': 'Atami Chijo Tengoku',
    '瑞雲郷': 'Zuiunkyo',
    '御講話': 'Gokouwa',
    'おひかり': 'Ohikari',
    '拝啓': 'Haikei',
    '明主様': 'Meishu-sama',
    '論文集': 'Ronbunshu',
    '医学革命の書': 'Igaku Kakumei no Sho',
    '自然農法': 'Shizen Noho',
    '解説': 'Kaisetsu',
    '笑冠句集': 'Shokanku Shu',
}

def clean_text(text):
    if not text:
        return text
    
    # Simple replacement based on mapping (Longest keys first)
    sorted_keys = sorted(TERM_MAPPING.keys(), key=len, reverse=True)
    for key in sorted_keys:
        val = TERM_MAPPING[key]
        if key in text:
            # Case insensitive check for Portuguese could be better, but keys are mostly Capitalized in mapping
            text = text.replace(key, val)
    return text

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"Target file not found: {TARGET_FILE}")
        return

    print(f"Processing {TARGET_FILE}...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    
    # Target all anchor tags as they contain the titles in the table
    links = soup.find_all('a')
    for link in links:
        if link.string:
            new_text = clean_text(link.string)
            if new_text != link.string:
                print(f"Replacing: '{link.string}' -> '{new_text}'")
                link.string.replace_with(new_text)

    # Also target font tags inside cells that might not be links
    fonts = soup.find_all('font')
    for font in fonts:
        if font.string:
            new_text = clean_text(font.string)
            if new_text != font.string:
                print(f"Replacing: '{font.string}' -> '{new_text}'")
                font.string.replace_with(new_text)

    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print("Done.")

if __name__ == "__main__":
    main()
