import asyncio
import ollama
import edge_tts
import os
import json


# =========================
# CONFIGURAÇÕES
# =========================

MODELO = "llama3.1:8b"

VOZ = "pt-BR-FranciscaNeural"

PASTA_AUDIOS = "audios"

PASTA_TEMPOS = "tempos_palavras"


# =========================
# FUNÇÃO PRINCIPAL
# =========================

def gerar_narracao(tema):

    # =========================
    # PROMPT
    # =========================

    prompt = f"""
Crie um roteiro de aproximadamente 30 segundos
para um Short sobre:

{tema}

Divida o roteiro em exatamente 5 cenas.

Para cada cena use EXATAMENTE:

CENA 1
NARRAÇÃO: texto da narração
VISUAL: descrição visual

CENA 2
NARRAÇÃO: texto da narração
VISUAL: descrição visual

CENA 3
NARRAÇÃO: texto da narração
VISUAL: descrição visual

CENA 4
NARRAÇÃO: texto da narração
VISUAL: descrição visual

CENA 5
NARRAÇÃO: texto da narração
VISUAL: descrição visual

REGRAS:

- Exatamente 5 cenas.
- Não escreva introdução.
- Não escreva conclusão fora das cenas.
- Não coloque comentários sobre o roteiro.
- Escreva em português.
- A narração deve ser natural.
- Cada cena deve ter aproximadamente 5 a 8 segundos.
- O conteúdo deve ser relacionado ao tema.
- A descrição VISUAL deve representar exatamente o que está sendo narrado.
"""

    print(
        f"\nTema recebido pela IA: {tema}"
    )

    print(
        "\nGerando roteiro...\n"
    )


    # =========================
    # GERAR ROTEIRO COM OLLAMA
    # =========================

    resposta = ollama.chat(

        model=MODELO,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    roteiro = resposta[
        "message"
    ][
        "content"
    ]


    # =========================
    # MOSTRAR ROTEIRO
    # =========================

    print(
        "========== ROTEIRO ==========\n"
    )

    print(roteiro)


    # =========================
    # EXTRAIR NARRAÇÕES
    # =========================

    linhas = roteiro.splitlines()

    narracoes = []

    for linha in linhas:

        linha = linha.strip()

        if "NARRAÇÃO:" in linha.upper():

            texto = linha.split(
                ":",
                1
            )[1].strip()


            # Remove aspas
            texto = texto.strip(
                '"'
            )


            if texto:

                narracoes.append(
                    texto
                )


    # =========================
    # VERIFICAR CENAS
    # =========================

    if len(narracoes) != 5:

        print(
            f"\nERRO: a IA criou "
            f"{len(narracoes)} cenas em vez de 5."
        )

        return None


    # =========================
    # MOSTRAR NARRAÇÕES
    # =========================

    print(
        "\n========== NARRAÇÕES ==========\n"
    )


    for numero, texto in enumerate(
        narracoes,
        1
    ):

        print(
            f"CENA {numero}:"
        )

        print(texto)

        print()


    # =========================
    # CRIAR PASTAS
    # =========================

    os.makedirs(
        PASTA_AUDIOS,
        exist_ok=True
    )

    os.makedirs(
        PASTA_TEMPOS,
        exist_ok=True
    )


    # =========================
    # GERAR ÁUDIOS
    # =========================

    print(
        "\n========== GERANDO ÁUDIOS ==========\n"
    )


    sucesso = asyncio.run(
        gerar_audios(
            narracoes
        )
    )


    # =========================
    # VERIFICAR
    # =========================

    if not sucesso:

        print(
            "\nNão foi possível gerar todos "
            "os áudios."
        )

        return None


    # =========================
    # GERAR SRT
    # =========================

    srt_ok = gerar_srt()

    if not srt_ok:

        print(
            "\nNão foi possível gerar "
            "as legendas."
        )

        return None


    # =========================
    # RESULTADO
    # =========================

    print(
        "\n=============================="
    )

    print(
        "NARRAÇÕES + TEMPOS + LEGENDAS CRIADOS!"
    )

    print(
        "=============================="
    )


    for numero in range(
        1,
        6
    ):

        audio = os.path.join(
            PASTA_AUDIOS,
            f"cena_{numero}.mp3"
        )

        tempos = os.path.join(
            PASTA_TEMPOS,
            f"cena_{numero}.json"
        )


        if os.path.exists(audio):

            tamanho = os.path.getsize(
                audio
            )

            print(
                f"CENA {numero}: "
                f"áudio OK "
                f"({tamanho} bytes)"
            )


        if os.path.exists(tempos):

            print(
                f"CENA {numero}: "
                f"tempos OK"
            )


    print(
        "\nLegenda criada: legendas.srt"
    )


    return roteiro


# =========================
# GERAR ÁUDIOS
# =========================

async def gerar_audios(narracoes):

    # =========================
    # CADA CENA
    # =========================

    for numero, texto in enumerate(
        narracoes,
        1
    ):

        arquivo_audio = os.path.join(
            PASTA_AUDIOS,
            f"cena_{numero}.mp3"
        )

        arquivo_tempos = os.path.join(
            PASTA_TEMPOS,
            f"cena_{numero}.json"
        )


        print(
            f"\nGerando áudio da CENA {numero}..."
        )


        sucesso = False


        # =========================
        # 3 TENTATIVAS
        # =========================

        for tentativa in range(
            1,
            4
        ):

            try:

                print(
                    f"Tentativa {tentativa}/3..."
                )


                comunicacao = edge_tts.Communicate(

                    text=texto,

                    voice=VOZ,

                    boundary="WordBoundary"
                )


                palavras = []


                # =========================
                # RECEBER ÁUDIO
                # =========================

                with open(
                    arquivo_audio,
                    "wb"
                ) as audio:

                    async for evento in comunicacao.stream():

                        # =========================
                        # ÁUDIO
                        # =========================

                        if evento[
                            "type"
                        ] == "audio":

                            audio.write(
                                evento["data"]
                            )


                        # =========================
                        # PALAVRA
                        # =========================

                        elif evento[
                            "type"
                        ] == "WordBoundary":

                            inicio = (
                                evento["offset"]
                                / 10_000_000
                            )


                            duracao = (
                                evento["duration"]
                                / 10_000_000
                            )


                            fim = (
                                inicio
                                + duracao
                            )


                            palavras.append(
                                {
                                    "palavra":
                                        evento["text"],

                                    "inicio":
                                        round(
                                            inicio,
                                            3
                                        ),

                                    "fim":
                                        round(
                                            fim,
                                            3
                                        )
                                }
                            )


                # =========================
                # VERIFICAR
                # =========================

                if (
                    os.path.exists(
                        arquivo_audio
                    )
                    and os.path.getsize(
                        arquivo_audio
                    ) > 0
                    and len(palavras) > 0
                ):

                    sucesso = True


                    print(
                        "Áudio gerado com sucesso!"
                    )


                    # =========================
                    # SALVAR TEMPOS
                    # =========================

                    with open(
                        arquivo_tempos,
                        "w",
                        encoding="utf-8"
                    ) as arquivo:

                        json.dump(
                            palavras,
                            arquivo,
                            ensure_ascii=False,
                            indent=4
                        )


                    print(
                        f"Áudio salvo: "
                        f"{arquivo_audio}"
                    )


                    print(
                        f"Tempos salvos: "
                        f"{arquivo_tempos}"
                    )


                    # =========================
                    # MOSTRAR PALAVRAS
                    # =========================

                    print(
                        f"\n========== CENA {numero} =========="
                    )


                    for palavra in palavras:

                        print(
                            f'{palavra["palavra"]:<20} '
                            f'{palavra["inicio"]:>6.2f}s '
                            f'→ '
                            f'{palavra["fim"]:>6.2f}s'
                        )


                    break


            except Exception as erro:

                print(
                    f"\nErro na tentativa "
                    f"{tentativa}/3:"
                )

                print(erro)


                # =========================
                # APAGAR ARQUIVO
                # =========================

                if os.path.exists(
                    arquivo_audio
                ):

                    try:

                        os.remove(
                            arquivo_audio
                        )

                    except OSError:

                        pass


                if tentativa < 3:

                    print(
                        "Tentando novamente "
                        "em 2 segundos..."
                    )

                    await asyncio.sleep(
                        2
                    )


        # =========================
        # CENA FALHOU
        # =========================

        if not sucesso:

            print(
                f"\nERRO: não foi possível "
                f"gerar a CENA {numero}."
            )

            return False


    # =========================
    # TODAS AS CENAS OK
    # =========================

    return True


# =========================
# CONVERTER SEGUNDOS PARA SRT
# =========================

def segundos_para_srt(segundos):

    horas = int(
        segundos // 3600
    )

    minutos = int(
        (segundos % 3600) // 60
    )

    segundos_inteiros = int(
        segundos % 60
    )

    milissegundos = int(
        round(
            (segundos - int(segundos))
            * 1000
        )
    )


    # =========================
    # CORRIGIR 1000 MILISSEGUNDOS
    # =========================

    if milissegundos >= 1000:

        segundos_inteiros += 1

        milissegundos -= 1000


    # =========================
    # CORRIGIR 60 SEGUNDOS
    # =========================

    if segundos_inteiros >= 60:

        minutos += 1

        segundos_inteiros -= 60


    # =========================
    # CORRIGIR 60 MINUTOS
    # =========================

    if minutos >= 60:

        horas += 1

        minutos -= 60


    return (
        f"{horas:02d}:"
        f"{minutos:02d}:"
        f"{segundos_inteiros:02d},"
        f"{milissegundos:03d}"
    )


# =========================
# GERAR SRT SINCRONIZADO
# =========================

def gerar_srt():

    print(
        "\n=============================="
    )

    print(
        "GERANDO LEGENDAS SINCRONIZADAS"
    )

    print(
        "==============================\n"
    )


    legendas = []

    tempo_acumulado = 0


    # =========================
    # CADA CENA
    # =========================

    for numero_cena in range(
        1,
        6
    ):

        arquivo_tempos = os.path.join(
            PASTA_TEMPOS,
            f"cena_{numero_cena}.json"
        )


        if not os.path.exists(
            arquivo_tempos
        ):

            print(
                f"ERRO: {arquivo_tempos} "
                f"não encontrado."
            )

            return False


        with open(
            arquivo_tempos,
            "r",
            encoding="utf-8"
        ) as arquivo:

            palavras = json.load(
                arquivo
            )


        if not palavras:

            print(
                f"ERRO: CENA {numero_cena} "
                f"não possui tempos."
            )

            return False


        # =========================
        # AGRUPAR PALAVRAS
        # =========================

        grupo = []

        inicio_grupo = None

        fim_grupo = None

        ultimo_fim = None


        for palavra in palavras:

            texto = str(
                palavra["palavra"]
            ).strip()


            inicio = (
                palavra["inicio"]
                + tempo_acumulado
            )

            fim = (
                palavra["fim"]
                + tempo_acumulado
            )


            # =========================
            # PRIMEIRA PALAVRA
            # =========================

            if not grupo:

                grupo = [
                    texto
                ]

                inicio_grupo = inicio

                fim_grupo = fim

                ultimo_fim = fim

                continue


            # =========================
            # CALCULAR PAUSA
            # =========================

            pausa = (
                inicio
                - ultimo_fim
            )


            texto_atual = " ".join(
                grupo
            )


            # =========================
            # DECIDIR SE QUEBRA
            # =========================

            if (
                pausa > 0.35
                or len(grupo) >= 5
                or len(texto_atual) > 42
            ):

                legendas.append(
                    {
                        "inicio":
                            inicio_grupo,

                        "fim":
                            fim_grupo,

                        "texto":
                            texto_atual
                    }
                )


                grupo = [
                    texto
                ]

                inicio_grupo = inicio

                fim_grupo = fim

            else:

                grupo.append(
                    texto
                )

                fim_grupo = fim


            ultimo_fim = fim


        # =========================
        # ÚLTIMO GRUPO
        # =========================

        if grupo:

            legendas.append(
                {
                    "inicio":
                        inicio_grupo,

                    "fim":
                        fim_grupo,

                    "texto":
                        " ".join(grupo)
                }
            )


        # =========================
        # TEMPO DA CENA
        # =========================

        ultimo_tempo = max(
            palavra["fim"]
            for palavra in palavras
        )


        tempo_acumulado += (
            ultimo_tempo
        )


    # =========================
    # SALVAR SRT
    # =========================

    try:

        with open(
            "legendas.srt",
            "w",
            encoding="utf-8"
        ) as arquivo:

            for numero, legenda in enumerate(
                legendas,
                1
            ):

                arquivo.write(
                    f"{numero}\n"
                )

                arquivo.write(
                    f"{segundos_para_srt(legenda['inicio'])}"
                    f" --> "
                    f"{segundos_para_srt(legenda['fim'])}\n"
                )

                arquivo.write(
                    f"{legenda['texto']}\n\n"
                )


    except Exception as erro:

        print(
            f"ERRO ao criar SRT: {erro}"
        )

        return False


    # =========================
    # RESULTADO
    # =========================

    print(
        f"SRT criado com "
        f"{len(legendas)} legendas."
    )

    print(
        "Arquivo: legendas.srt"
    )


    return True