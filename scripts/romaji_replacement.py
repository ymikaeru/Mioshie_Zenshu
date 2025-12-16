#!/usr/bin/env python3
"""
Script to replace Portuguese translated book/source names with Romaji
across all HTML files in the project.
"""

import os
import re

# Define the replacements - Portuguese -> Romaji
REPLACEMENTS = {
    # Full book names
    'Coletânea de Textos do Mestre Jikan Okada': 'Jikan Okada Sensei Bunshu',
    'Coletânea de Ensaios do Mestre Jikan Okada': 'Jikan Okada Sensei Ronbunshu',
    'Coletânea de Ensinamentos': 'Mioshieshu',
    'Coletânea de Ensinamentos Sagrados': 'Goshinso Shu',
    'Registro de Ensinamentos': 'Gosuijiroku',
    'Registro de Palestras de Luz': 'Ohikari Kowa Roku',
    'Registro dos Ensinamentos Sagrados': 'Goshinso Roku',
    'Registro dos Ensinamentos Divinos': 'Goshimpo Roku',
    'Luz da Sabedoria Divina': 'Hikari no Chie',
    'Curso de Johrei': 'Johrei Ho Koza',
    'Guia de Difusão': 'Dendo no Shiori',
    'A Medicina do Amanhã': 'Ashita no Ijutsu',
    'Medicina do Amanhã': 'Ashita no Ijutsu',
    'Paraíso Terrestre': 'Chijo Tengoku',
    'Evangelho do Céu': 'Tengoku no Fukuin',
    'Salvação': 'Kyusei',
    'Glória': 'Eiko',
    'Luz': 'Hikari',
    'Criação da Civilização': 'Bunmei no Sozou',
    'Vida Saudável': 'Kenko Seikatsu',
    'Saúde e Medicina': 'Iryo to Kenko',
    'Agricultura Natural': 'Shizen Noho',
    'Explicação da Agricultura Natural': 'Shizen Noho Kaisetsu',
    'Método de Cultivo Sem Fertilizantes': 'Muhiryo Saibaiho',
    'O Poder da Terra': 'Tsuchi no Iryoku',
    'História de Milagres': 'Kiseki Monogatari',
    'O Verdadeiro Deus': 'Shin no Kami',
    'Anotações da Perseguição': 'Honan Shuki',
    'Crítica à Igreja Messias': 'Meshiya Kyo Hihan',
    'Minha História': 'Watashi Monogatari',
    'Vento nos Pinheiros': 'Matsukaze',
    'Luz Auspiciosa': 'Zuiko',
    'Boletim': 'Kaiho',
    
    # Common phrases - Portuguese -> Romaji
    'Orientações Divinas': 'Goshinji',
    'Volume': 'Kan',
}

def process_file(filepath):
    """Process a single HTML file and apply replacements."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0
    
    original_content = content
    changes = 0
    
    for pt, romaji in REPLACEMENTS.items():
        if pt in content:
            content = content.replace(pt, romaji)
            changes += 1
    
    if changes > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Updated: {os.path.basename(filepath)} ({changes} replacements)")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return 0
    
    return changes

def main():
    # Directories to process
    directories = [
        'filetop',
        'hakkousi',
        'miosie', 
        'kanren',
        'sasshi',
        'search1',
        'search2',
        'gosuiji'
    ]
    
    total_files = 0
    total_changes = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        print(f"\nProcessing {directory}/...")
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.html'):
                    filepath = os.path.join(root, filename)
                    changes = process_file(filepath)
                    if changes > 0:
                        total_files += 1
                        total_changes += changes
    
    print(f"\n{'='*50}")
    print(f"Total files updated: {total_files}")
    print(f"Total replacements: {total_changes}")

if __name__ == '__main__':
    main()
