import json
import sys
import re
sys.path.append('src')
from woodpecker.core.chunker import chunk_with_overlap, estimate_tokens, split_by_sentences, _split_long_sentence
text = [c['text'] for c in json.load(open('output_full.json', encoding='utf-8')) if c['token_count'] == 399][0]
print(f'Sentences: {len(split_by_sentences(text))}')
print(f'Subsentences: {len(_split_long_sentence(text, 200))}')

