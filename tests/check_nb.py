import json
with open(r'c:\Users\User\Downloads\Logex_WCN\notebook.ipynb', 'r', encoding='utf-8') as f:
    data = json.load(f)
for cell in data.get('cells', []):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'def pick_best' in source:
            print("--- CELL START ---")
            print(source[source.find('def pick_best'):source.find('def pick_best')+300])
            print("--- CELL END ---")
