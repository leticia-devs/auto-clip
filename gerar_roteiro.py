import ollama

import ollama

tema = input('Qual é o tema do Short? ')

prompt = f'''
Crie um roteiro de 30 segundos para um Short sobre: {tema}

Divida o roteiro em 5 cenas de aproximadamente 6 segundos.

Para cada cena informe:

CENA:
NARRAÇÃO:
VISUAL:

A narração deve ser curta e interessante.
O visual deve descrever o que deve aparecer na imagem ou vídeo.
Escreva em português.
'''

resposta = ollama.chat(
    model='llama3.1:8b',
    messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ]
)

print('\n' + resposta['message']['content'])