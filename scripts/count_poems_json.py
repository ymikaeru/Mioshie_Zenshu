import json

json_path = '/Users/michael/Documents/Ensinamentos/EnsinamentosAll/Data/poems.json'

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Total entries in poems.json: {len(data)}")
    
    # Check first and last titles to verify alignment
    if data:
        print(f"First: {data[0].get('title', 'No Title')}")
        print(f"Last: {data[-1].get('title', 'No Title')}")
except Exception as e:
    print(f"Error: {e}")
