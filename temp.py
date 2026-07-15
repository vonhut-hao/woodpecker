import json
for c in json.load(open('output_full.json', encoding='utf-8')):
 if c['token_count'] > 200:
  print(f"Length {c['token_count']}: {c['text'][:100]}...")
