import json
import os
import subprocess


# =========================
# CONFIGURAÇÕES
# =========================

PASTA_TEMPOS = "tempos_palavras"

PASTA_AUDIOS = "audios"

ARQUIVO_SRT = "legendas.srt"

NUM_CENAS = 5

# Quantidade máxima de palavras por legenda
MAX_PALAVRAS = 6

# Duração máxima de uma legenda
MAX_DURACAO = 2.5

# Se houver uma pausa maior que esse valor,
# a legenda anterior termina antes da pausa.
PAUSA_MAXIMA = 0.30


# =========================
# CONVERTER SEGUNDOS → SRT
# =========================

def segundos_para_srt(segundos):

    horas = int(segundos // 3600)

    minutos = int(
        (segundos % 3600) // 60
    )

    segundos_inteiros = int(
        segundos % 60
    )

    milissegundos = int(
        round(
            (segundos - int(segundos)) * 1000
        )
    )

    # Corrigir caso arredondamento dê 1000 ms
    if milissegundos >= 1000:

        milissegundos = 0

        segundos_inteiros += 1


    if segundos_inteiros >= 60:

        segundos_inteiros = 0

        minutos += 1


    if minutos >= 60:

        minutos = 0

        horas += 1


    return (
        f"{horas:02d}:"
        f"{minutos:02d}:"
        f"{segundos_inteiros:02d},"
        f"{milissegundos:03d}"
    )


# =========================
# OBTER DURAÇÃO DO ÁUDIO
# =========================

def obter_duracao_audio(arquivo):

    comando = [

        "ffprobe",

        "-v",
        "error",

        "-show_entries",
        "format=duration",

        "-of",
        "default=noprint_wrappers=1:nokey=1",

        arquivo
    ]


    resultado = subprocess.run(

        comando,

        capture_output=True,

        text=True
    )


    if resultado.returncode != 0:

        return None


    try:

        return float(
            resultado.stdout.strip()
        )

    except ValueError:

        return None


# =========================
# LER TEMPOS DO WHISPERX
# =========================

def ler_tempos_cena(numero):

    arquivo = os.path.join(

        PASTA_TEMPOS,

        f"cena_{numero}.json"
    )


    if not os.path.exists(arquivo):

        print(
            f"ERRO: arquivo não encontrado:"
        )

        print(arquivo)

        return None


    try:

        with open(

            arquivo,

            "r",

            encoding="utf-8"
        ) as arquivo_json:

            palavras = json.load(
                arquivo_json
            )


    except Exception as erro:

        print(
            f"ERRO ao ler {arquivo}:"
        )

        print(erro)

        return None


    return palavras


# =========================
# CRIAR GRUPOS DE LEGENDAS
# =========================

def criar_grupos(palavras):

    grupos = []

    grupo_atual = []


    for palavra in palavras:

        if not grupo_atual:

            grupo_atual.append(
                palavra
            )

            continue


        ultima = grupo_atual[-1]


        inicio_atual = float(
            palavra["inicio"]
        )

        fim_ultima = float(
            ultima["fim"]
        )


        pausa = (
            inicio_atual
            - fim_ultima
        )


        inicio_grupo = float(
            grupo_atual[0]["inicio"]
        )


        duracao_grupo = (
            float(palavra["fim"])
            - inicio_grupo
        )


        # =========================
        # VERIFICAR SE DEVE DIVIDIR
        # =========================

        deve_dividir = False


        # Pausa significativa
        if pausa > PAUSA_MAXIMA:

            deve_dividir = True


        # Muitas palavras
        if len(grupo_atual) >= MAX_PALAVRAS:

            deve_dividir = True


        # Legenda muito longa
        if duracao_grupo > MAX_DURACAO:

            deve_dividir = True


        if deve_dividir:

            grupos.append(
                grupo_atual
            )

            grupo_atual = [
                palavra
            ]

        else:

            grupo_atual.append(
                palavra
            )


    # Último grupo

    if grupo_atual:

        grupos.append(
            grupo_atual
        )


    return grupos


# =========================
# TRANSFORMAR GRUPOS EM LEGENDAS
# =========================

def criar_legendas_cena(

    palavras,

    numero_cena,

    deslocamento
):

    grupos = criar_grupos(
        palavras
    )


    legendas = []


    for grupo in grupos:

        if not grupo:

            continue


        inicio = (

            float(
                grupo[0]["inicio"]
            )

            + deslocamento
        )


        fim = (

            float(
                grupo[-1]["fim"]
            )

            + deslocamento
        )


        texto = " ".join(

            str(
                palavra["palavra"]
            ).strip()

            for palavra in grupo
        )


        texto = texto.strip()


        if not texto:

            continue


        legendas.append(

            {
                "inicio": inicio,

                "fim": fim,

                "texto": texto
            }
        )


    return legendas


# =========================
# SALVAR SRT
# =========================

def salvar_srt(legendas):

    print()

    print(
        "=============================="
    )

    print(
        "SALVANDO SRT"
    )

    print(
        "=============================="
    )

    print()


    try:

        with open(

            ARQUIVO_SRT,

            "w",

            encoding="utf-8"
        ) as arquivo:

            for numero, legenda in enumerate(

                legendas,

                1
            ):

                inicio = legenda["inicio"]

                fim = legenda["fim"]

                texto = legenda["texto"]


                inicio_srt = segundos_para_srt(

                    inicio
                )


                fim_srt = segundos_para_srt(

                    fim
                )


                arquivo.write(

                    f"{numero}\n"
                )


                arquivo.write(

                    f"{inicio_srt} --> {fim_srt}\n"
                )


                arquivo.write(

                    f"{texto}\n"
                )


                arquivo.write(
                    "\n"
                )


    except Exception as erro:

        print()

        print(
            "ERRO ao salvar SRT:"
        )

        print(erro)

        return False


    print(
        "=============================="
    )

    print(
        "SRT CRIADO COM SUCESSO!"
    )

    print(
        "=============================="
    )

    print(
        f"Arquivo: {ARQUIVO_SRT}"
    )

    print(
        f"Total de legendas: "
        f"{len(legendas)}"
    )


    return True


# =========================
# FUNÇÃO PRINCIPAL
# =========================

def criar_legendas():

    print()

    print(
        "=============================="
    )

    print(
        "CRIADOR DE LEGENDAS WHISPERX"
    )

    print(
        "=============================="
    )

    print()


    todas_legendas = []

    deslocamento = 0.0


    # =========================
    # PROCESSAR CENAS
    # =========================

    for numero in range(

        1,

        NUM_CENAS + 1
    ):

        print()

        print(
            f"Lendo tempos da CENA {numero}..."
        )


        palavras = ler_tempos_cena(

            numero
        )


        if palavras is None:

            return False


        print(

            f"  {len(palavras)} "
            f"palavras encontradas."
        )


        # =========================
        # DURAÇÃO DO ÁUDIO
        # =========================

        arquivo_audio = os.path.join(

            PASTA_AUDIOS,

            f"cena_{numero}.mp3"
        )


        if not os.path.exists(

            arquivo_audio
        ):

            print()

            print(
                f"ERRO: áudio não encontrado:"
            )

            print(
                arquivo_audio
            )

            return False


        duracao = obter_duracao_audio(

            arquivo_audio
        )


        if duracao is None:

            print()

            print(
                f"ERRO: não foi possível "
                f"obter a duração da CENA {numero}."
            )

            return False


        print(

            f"  Duração do áudio: "
            f"{duracao:.3f}s"
        )


        # =========================
        # CRIAR LEGENDAS DA CENA
        # =========================

        print()

        print(
            f"Processando CENA {numero}..."
        )


        legendas_cena = criar_legendas_cena(

            palavras,

            numero,

            deslocamento
        )


        # =========================
        # MOSTRAR LEGENDAS
        # =========================

        for legenda in legendas_cena:

            inicio = legenda["inicio"]

            fim = legenda["fim"]

            texto = legenda["texto"]


            print(

                f"{segundos_para_srt(inicio)}"
                f" --> "
                f"{segundos_para_srt(fim)}"
            )


            print(
                f"   {texto}"
            )


        todas_legendas.extend(

            legendas_cena
        )


        # =========================
        # AVANÇAR PARA PRÓXIMA CENA
        # =========================

        deslocamento += duracao


    # =========================
    # VERIFICAR
    # =========================

    if not todas_legendas:

        print()

        print(
            "ERRO: nenhuma legenda foi criada."
        )

        return False


    print()

    print(
        f"Total de legendas: "
        f"{len(todas_legendas)}"
    )


    # =========================
    # SALVAR
    # =========================

    sucesso = salvar_srt(

        todas_legendas
    )


    return sucesso


# =========================
# EXECUTAR
# =========================

if __name__ == "__main__":

    criar_legendas()