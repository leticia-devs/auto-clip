import ollama
import json
import re

tema = input('Qual é o tema do Short? ')


# ==============================
# 1. GERAR ROTEIRO
# ==============================

prompt = f'''
Crie um roteiro de aproximadamente 30 segundos
para um Short sobre:

{tema}

Divida o roteiro em exatamente 5 cenas.

Para cada cena use EXATAMENTE este formato:

CENA 1
NARRAÇÃO: texto da narração
VISUAL: descrição objetiva da imagem que deve aparecer

CENA 2
NARRAÇÃO: texto da narração
VISUAL: descrição objetiva da imagem que deve aparecer

Continue até a CENA 5.

REGRAS:

- A narração deve ser curta, natural e interessante.
- Cada cena deve ter aproximadamente 5 a 7 segundos.
- O visual deve representar diretamente o que está sendo narrado.
- Descreva pessoas, lugares, objetos e acontecimentos visíveis.
- Não coloque explicações sobre a imagem.
- Não coloque palavras como "VISUAL:" dentro da descrição.
- Escreva tudo em português.
'''

print('\nGerando roteiro...\n')


resposta = ollama.chat(
    model='llama3.1:8b',
    messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ]
)


roteiro = resposta['message']['content']


print('========== ROTEIRO ==========\n')
print(roteiro)


# ==============================
# 2. EXTRAIR CENAS
# ==============================

padrao = re.compile(
    r'CENA\s*(\d+).*?'
    r'NARRAÇÃO:\s*(.*?)\s*'
    r'VISUAL:\s*(.*?)(?=\s*CENA\s*\d+|\Z)',
    re.IGNORECASE | re.DOTALL
)


resultados = padrao.findall(roteiro)


if len(resultados) < 5:

    print('\nERRO: não foi possível encontrar as 5 cenas.')
    print(f'Cenas encontradas: {len(resultados)}')
    print('\nRoteiro recebido:')
    print(roteiro)

    exit()


# ==============================
# 3. CRIAR ESTRUTURA
# ==============================

cenas = []


for numero, narracao, visual in resultados[:5]:

    cena = {
        'numero': int(numero),
        'narracao': narracao.strip(),
        'visual': visual.strip()
    }

    cenas.append(cena)


# ==============================
# 4. MOSTRAR CENAS
# ==============================

print('\n========== CENAS ==========\n')


for cena in cenas:

    print(f"CENA {cena['numero']}")
    print(f"Narração: {cena['narracao']}")
    print(f"Visual: {cena['visual']}")
    print()


# ==============================
# 5. SALVAR ROTEIRO
# ==============================

dados = {
    'tema': tema,
    'cenas': cenas
}


with open("roteiro.json", "w", encoding="utf-8") as arquivo:

    json.dump(
        dados,
        arquivo,
        ensure_ascii=False,
        indent=4
    )


print('==============================')
print('ROTEIRO SALVO COM SUCESSO!')
print('==============================')
print('Arquivo: roteiro.json')
