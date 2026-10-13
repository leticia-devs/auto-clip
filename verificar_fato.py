import requests
import ollama

# =========================
# 1. Informações
# =========================

afirmacao = input('Digite uma afirmação histórica: ')
tema = input('Qual é o tema da afirmação? ')

# =========================
# 2. Pesquisar na Wikipedia
# =========================

resposta = requests.get(
    'https://pt.wikipedia.org/w/api.php',
    params={
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'explaintext': True,
        'titles': tema,
        'redirects': True
    },
    headers={
        'User-Agent': 'AutoClip/1.0'
    }
)

dados = resposta.json()

paginas = dados['query']['pages']

primeiro = next(iter(paginas.values()))

if 'extract' not in primeiro:
    print('\nNão foi possível encontrar uma fonte para esse tema.')
    exit()

texto_fonte = primeiro['extract']

print('\n--- FONTE ENCONTRADA ---')
print(primeiro['title'])

# =========================
# 3. Analisar com Ollama
# =========================

print('\n--- ANÁLISE DA IA ---')

prompt = f'''
Você é um verificador de fatos históricos.

Compare cuidadosamente a afirmação com a fonte.

AFIRMAÇÃO:
{afirmacao}

FONTE:
{texto_fonte}

Primeiro encontre na fonte informações que sejam
relevantes para a afirmação.

Depois classifique:

CONFIRMADO
A fonte apoia claramente a afirmação.

INCERTO
A fonte possui informações relacionadas, mas não
é possível confirmar ou negar completamente.

SEM_PROVAS
A fonte não fornece evidências suficientes para
confirmar a afirmação ou apresenta informações
que contradizem a afirmação.

IMPORTANTE:
Se a fonte apresentar uma informação que contradiz
a afirmação, NÃO classifique como CONFIRMADO.

Responda exatamente neste formato:

STATUS: CONFIRMADO, INCERTO ou SEM_PROVAS
EVIDENCIA: escreva a informação da fonte que foi usada
'''

resposta_ollama = ollama.chat(
    model='llama3.1:8b',
    messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ]
)

resultado = resposta_ollama['message']['content'].strip()

print(resultado)