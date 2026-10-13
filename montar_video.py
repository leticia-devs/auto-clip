import os
import subprocess
import sys


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_AUDIOS = "audios"

PASTA_IMAGENS = "imagens"

ARQUIVO_LEGENDAS = "legendas.srt"

PASTA_TEMP = "temp_video"

ARQUIVO_FINAL = "video_final.mp4"

NUM_CENAS = 5


# ============================================================
# FUNÇÃO PARA EXECUTAR COMANDOS
# ============================================================

def executar_comando(comando):

    print()
    print("Executando:")

    print(" ".join(comando))

    print()

    resultado = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if resultado.returncode != 0:

        print()
        print("ERRO AO EXECUTAR FFMPEG")
        print()
        print(resultado.stdout)

        return False

    return True


# ============================================================
# ENCONTRAR IMAGEM DA CENA
# ============================================================

def encontrar_imagem(numero):

    extensoes = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]

    nomes_possiveis = [

        f"cena_{numero}",

        f"cena{numero}",

        f"scene_{numero}",

        f"scene{numero}"

    ]

    pastas_possiveis = [

        PASTA_IMAGENS,

        "visuais",

        "images",

        "imagens_geradas",

        "visuais_gerados"

    ]


    for pasta in pastas_possiveis:

        if not os.path.exists(pasta):
            continue


        for nome in nomes_possiveis:

            for extensao in extensoes:

                caminho = os.path.join(
                    pasta,
                    nome + extensao
                )

                if os.path.exists(caminho):

                    return caminho


    return None


# ============================================================
# ENCONTRAR ÁUDIO
# ============================================================

def encontrar_audio(numero):

    extensoes = [
        ".mp3",
        ".wav",
        ".m4a"
    ]


    for extensao in extensoes:

        caminho = os.path.join(
            PASTA_AUDIOS,
            f"cena_{numero}{extensao}"
        )

        if os.path.exists(caminho):

            return caminho


    return None


# ============================================================
# OBTER DURAÇÃO DO ÁUDIO
# ============================================================

def obter_duracao(caminho):

    comando = [

        "ffprobe",

        "-v",
        "error",

        "-show_entries",
        "format=duration",

        "-of",
        "default=noprint_wrappers=1:nokey=1",

        caminho
    ]


    resultado = subprocess.run(

        comando,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True,

        encoding="utf-8",

        errors="replace"
    )


    if resultado.returncode != 0:

        return None


    try:

        return float(
            resultado.stdout.strip()
        )

    except ValueError:

        return None


# ============================================================
# CRIAR PASTA TEMPORÁRIA
# ============================================================

def preparar_pasta():

    os.makedirs(
        PASTA_TEMP,
        exist_ok=True
    )


# ============================================================
# APAGAR VÍDEOS TEMPORÁRIOS ANTIGOS
# ============================================================

def limpar_temporarios():

    if not os.path.exists(PASTA_TEMP):

        return


    for arquivo in os.listdir(PASTA_TEMP):

        caminho = os.path.join(
            PASTA_TEMP,
            arquivo
        )


        if os.path.isfile(caminho):

            try:

                os.remove(caminho)

            except Exception:

                pass


# ============================================================
# CRIAR UMA CENA
# ============================================================

def criar_cena(numero):

    imagem = encontrar_imagem(numero)

    audio = encontrar_audio(numero)


    print()
    print("==============================")
    print(f"CENA {numero}")
    print("==============================")


    # --------------------------------------------------------
    # VERIFICAR IMAGEM
    # --------------------------------------------------------

    if imagem is None:

        print()
        print(
            f"ERRO: não encontrei a imagem da CENA {numero}."
        )

        print()
        print(
            "Pastas procuradas:"
        )

        print(
            "imagens/"
        )

        print(
            "visuais/"
        )

        print(
            "images/"
        )

        print(
            "imagens_geradas/"
        )

        print(
            "visuais_gerados/"
        )

        return None


    # --------------------------------------------------------
    # VERIFICAR ÁUDIO
    # --------------------------------------------------------

    if audio is None:

        print()

        print(
            f"ERRO: não encontrei o áudio da CENA {numero}."
        )

        return None


    print()
    print(
        f"Imagem: {imagem}"
    )

    print(
        f"Áudio: {audio}"
    )


    # --------------------------------------------------------
    # DURAÇÃO
    # --------------------------------------------------------

    duracao = obter_duracao(audio)


    if duracao is None:

        print(
            "ERRO: não consegui descobrir "
            "a duração do áudio."
        )

        return None


    print(
        f"Duração: {duracao:.3f} segundos"
    )


    # --------------------------------------------------------
    # ARQUIVO DE SAÍDA
    # --------------------------------------------------------

    arquivo_saida = os.path.join(

        PASTA_TEMP,

        f"cena_{numero}.mp4"

    )


    # --------------------------------------------------------
    # FFMPEG
    # --------------------------------------------------------

    comando = [

        "ffmpeg",

        "-y",

        "-loop",
        "1",

        "-i",
        imagem,

        "-i",
        audio,

        "-t",
        str(duracao),

        "-map",
        "0:v:0",

        "-map",
        "1:a:0",

        "-c:v",
        "libx264",

        "-preset",
        "ultrafast",

        "-pix_fmt",
        "yuv420p",

        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        arquivo_saida
    ]


    sucesso = executar_comando(
        comando
    )


    if not sucesso:

        return None


    if not os.path.exists(
        arquivo_saida
    ):

        print(
            "ERRO: vídeo da cena não foi criado."
        )

        return None


    print()
    print(
        f"✓ CENA {numero} criada!"
    )


    return arquivo_saida


# ============================================================
# CRIAR LISTA PARA CONCATENAÇÃO
# ============================================================

def criar_lista_concat(videos):

    arquivo_lista = os.path.join(

        PASTA_TEMP,

        "lista.txt"

    )


    with open(

        arquivo_lista,

        "w",

        encoding="utf-8"

    ) as arquivo:


        for video in videos:

            caminho_absoluto = os.path.abspath(
                video
            )


            # FFMPEG no Windows aceita caminho
            # com barras normais quando usamos
            # o formato abaixo.

            caminho_absoluto = (
                caminho_absoluto
                .replace("\\", "/")
            )


            arquivo.write(
                f"file '{caminho_absoluto}'\n"
            )


    return arquivo_lista


# ============================================================
# JUNTAR CENAS
# ============================================================

def juntar_cenas(videos):

    print()
    print("==============================")
    print("JUNTANDO CENAS")
    print("==============================")


    lista = criar_lista_concat(
        videos
    )


    video_sem_legenda = os.path.join(

        PASTA_TEMP,

        "video_sem_legenda.mp4"

    )


    comando = [

        "ffmpeg",

        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        lista,

        "-c",
        "copy",

        video_sem_legenda

    ]


    sucesso = executar_comando(
        comando
    )


    if not sucesso:

        return None


    if not os.path.exists(
        video_sem_legenda
    ):

        print(
            "ERRO: vídeo final sem legenda não foi criado."
        )

        return None


    print()
    print(
        "✓ Cenas juntadas com sucesso!"
    )


    return video_sem_legenda


# ============================================================
# COLOCAR LEGENDAS
# ============================================================

def colocar_legendas(video):

    print()
    print("==============================")
    print("ADICIONANDO LEGENDAS")
    print("==============================")


    if not os.path.exists(
        ARQUIVO_LEGENDAS
    ):

        print()
        print(
            f"ERRO: arquivo {ARQUIVO_LEGENDAS} não encontrado."
        )

        return False


    # --------------------------------------------------------
    # Caminho absoluto do SRT
    # --------------------------------------------------------

    legenda_absoluta = os.path.abspath(
        ARQUIVO_LEGENDAS
    )


    # --------------------------------------------------------
    # Escapar caminho para o filtro subtitles
    # --------------------------------------------------------

    legenda_filtro = (
        legenda_absoluta
        .replace("\\", "/")
        .replace(":", "\\:")
        .replace("'", "\\'")
    )


    # --------------------------------------------------------
    # Filtro das legendas
    # --------------------------------------------------------

    filtro = (
        f"subtitles='{legenda_filtro}':"
        "force_style="
        "'FontName=Arial,"
        "FontSize=18,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=120'"
    )


    # --------------------------------------------------------
    # FFMPEG
    # --------------------------------------------------------

    comando = [

        "ffmpeg",

        "-y",

        "-i",
        video,

        "-vf",
        filtro,

        "-c:v",
        "libx264",

        "-preset",
        "ultrafast",

        "-crf",
        "23",

        "-c:a",
        "copy",

        "-movflags",
        "+faststart",

        ARQUIVO_FINAL

    ]


    sucesso = executar_comando(
        comando
    )


    if not sucesso:

        return False


    if not os.path.exists(
        ARQUIVO_FINAL
    ):

        print()
        print(
            "ERRO: vídeo final não foi criado."
        )

        return False


    return True


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print()
    print("==============================")
    print("MONTADOR DE VÍDEO")
    print("==============================")
    print()


    # --------------------------------------------------------
    # VERIFICAR FFMPEG
    # --------------------------------------------------------

    print(
        "Verificando FFmpeg..."
    )


    try:

        resultado = subprocess.run(

            [
                "ffmpeg",
                "-version"
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            encoding="utf-8",

            errors="replace"
        )


        if resultado.returncode != 0:

            print()
            print(
                "ERRO: FFmpeg não está funcionando."
            )

            return


    except FileNotFoundError:

        print()
        print(
            "ERRO: FFmpeg não foi encontrado."
        )

        print(
            "Verifique se ele está instalado."
        )

        return


    print(
        "✓ FFmpeg OK"
    )


    # --------------------------------------------------------
    # PREPARAR TEMP
    # --------------------------------------------------------

    preparar_pasta()

    limpar_temporarios()


    # --------------------------------------------------------
    # CRIAR CENAS
    # --------------------------------------------------------

    videos = []


    for numero in range(
        1,
        NUM_CENAS + 1
    ):

        video = criar_cena(
            numero
        )


        if video is None:

            print()
            print(
                "PROCESSO CANCELADO."
            )

            return


        videos.append(
            video
        )


    # --------------------------------------------------------
    # JUNTAR
    # --------------------------------------------------------

    video_sem_legenda = juntar_cenas(
        videos
    )


    if video_sem_legenda is None:

        print()
        print(
            "PROCESSO CANCELADO."
        )

        return


    # --------------------------------------------------------
    # LEGENDAS
    # --------------------------------------------------------

    sucesso = colocar_legendas(
        video_sem_legenda
    )


    if not sucesso:

        print()
        print(
            "PROCESSO CANCELADO."
        )

        return


    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("==============================")
    print("VÍDEO CRIADO COM SUCESSO!")
    print("==============================")
    print()

    print(
        f"Arquivo: {ARQUIVO_FINAL}"
    )

    print()

    print(
        "✓ Áudios utilizados"
    )

    print(
        "✓ Imagens utilizadas"
    )

    print(
        "✓ Cenas montadas"
    )

    print(
        "✓ Legendas WhisperX adicionadas"
    )

    print()


# ============================================================
# INICIAR PROGRAMA
# ============================================================

if __name__ == "__main__":

    main()