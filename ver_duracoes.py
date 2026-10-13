import subprocess
import os


print("==============================")
print("DURAÇÃO DOS ÁUDIOS")
print("==============================\n")


for numero in range(1, 6):

    arquivo = f"audios/cena_{numero}.mp3"

    if not os.path.exists(arquivo):

        print(f"CENA {numero}: arquivo não encontrado")
        continue

    comando = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        arquivo
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    try:

        duracao = float(resultado.stdout.strip())

        print(
            f"CENA {numero}: "
            f"{duracao:.2f} segundos"
        )

    except:

        print(
            f"CENA {numero}: "
            "não foi possível descobrir a duração."
        )