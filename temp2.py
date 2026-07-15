import json
for c in json.load(open('output_full.json', encoding='utf-8')):
 if c['token_count'] == 399:
  print(c['text'])
