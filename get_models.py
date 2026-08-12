import json
import urllib.request
req = urllib.request.Request('https://openrouter.ai/api/v1/models')
with urllib.request.urlopen(req) as response:
    models = json.loads(response.read().decode())['data']
    gemini = [m['id'] for m in models if 'gemini' in m['id'].lower() and (m['id'].endswith(':free') or m['pricing']['prompt'] == '0')]
    print('Gemini Free models:', gemini)
    llama = [m['id'] for m in models if 'llama' in m['id'].lower() and (m['id'].endswith(':free') or m['pricing']['prompt'] == '0')]
    print('Llama Free models:', llama)

