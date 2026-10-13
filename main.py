import subprocess
import sys

from gerar_narracao import gerar_narracao
from buscar_visuais import buscar_visuais
from transcrever_audio import transcrever_audios


# =========================
# FUNÇÃO PARA EXECUTAR PY
# =========================

def executar_script(nome_arquivo):

    resultado = subprocess.run(
        [
            sys.executable,
            nome_arquivo
        ]
    )

    return resultado.returncode == 0


# =========================
# INÍCIO
# =========================

print()
print("================================")
print("          AUTOCLIP V1")
print("================================")
print()


# =========================
# ESCOLHER TEMA
# =========================

tema = input(
    "Qual é o tema do Short? "
)


if not tema.strip():

    print()
    print(
        "ERRO: nenhum tema foi informado."
    )

    sys.exit(1)


print()

print(
    f"Tema escolhido: {tema}"
)


# =========================
# ETAPA 1
# ROTEIRO + NARRAÇÃO
# =========================

print()
print("==============================")
print("ETAPA 1 - ROTEIRO E NARRAÇÃO")
print("==============================")
print()


roteiro = gerar_narracao(
    tema
)


if roteiro is None:

    print()
    print(
        "ERRO: não foi possível "
        "gerar o roteiro/narração."
    )

    sys.exit(1)


print()
print("==============================")
print("ETAPA 1 CONCLUÍDA!")
print("==============================")


# =========================
# ETAPA 2
# VISUAIS
# =========================

print()
print("==============================")
print("ETAPA 2 - VISUAIS")
print("==============================")
print()


sucesso_visuais = buscar_visuais(
    roteiro
)


if not sucesso_visuais:

    print()
    print(
        "ERRO: não foi possível "
        "criar os visuais."
    )

    sys.exit(1)


print()
print("==============================")
print("ETAPA 2 CONCLUÍDA!")
print("==============================")


# =========================
# ETAPA 3
# WHISPERX
# =========================

print()
print("==============================")
print("ETAPA 3 - WHISPERX")
print("==============================")
print()


sucesso_whisper = transcrever_audios()


if not sucesso_whisper:

    print()
    print(
        "ERRO: o WhisperX não conseguiu "
        "sincronizar os áudios."
    )

    sys.exit(1)


print()
print("==============================")
print("ETAPA 3 CONCLUÍDA!")
print("==============================")


# =========================
# ETAPA 4
# CRIAR LEGENDAS
# =========================

print()
print("==============================")
print("ETAPA 4 - LEGENDAS")
print("==============================")
print()


sucesso_legendas = executar_script(
    "criar_legendas.py"
)


if not sucesso_legendas:

    print()
    print(
        "ERRO: não foi possível "
        "criar as legendas."
    )

    sys.exit(1)


print()
print("==============================")
print("ETAPA 4 CONCLUÍDA!")
print("==============================")


# =========================
# ETAPA 5
# MONTAR VÍDEO
# =========================

print()
print("==============================")
print("ETAPA 5 - MONTANDO VÍDEO")
print("==============================")
print()


sucesso_video = executar_script(
    "montar_video.py"
)


if not sucesso_video:

    print()
    print(
        "ERRO: não foi possível "
        "montar o vídeo."
    )

    sys.exit(1)


# =========================
# FINAL
# =========================

print()
print("==============================")
print("       AUTOCLIP FINALIZADO!")
print("==============================")
print()


print(
    "Vídeo criado:"
)

print(
    "video_final.mp4"
)

print()
print("🎬 Processo concluído!")
print()