import asyncio
import edge_tts

texto = input('Digite o texto da narração: ')

voz = 'pt-BR-FranciscaNeural'

async def gerar_narracao():
    comunicacao = edge_tts.Communicate(
        texto,
        voz
    )

    await comunicacao.save('narracao.mp3')


asyncio.run(gerar_narracao())

print('\nNarração criada com sucesso!')
print('Arquivo: narracao.mp3')