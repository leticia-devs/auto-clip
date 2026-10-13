import whisperx
import json
import os


# =========================
# CONFIGURAÇÕES
# =========================

PASTA_AUDIOS = "audios"

PASTA_TEMPOS = "tempos_palavras"

MODELO = "small"

DEVICE = "cpu"

COMPUTE_TYPE = "int8"

NUM_CENAS = 5


# =========================
# TRANSCRIBIR ÁUDIO
# =========================

def transcrever_audios():

    print()
    print("==============================")
    print("WHISPERX - SINCRONIZAÇÃO")
    print("==============================")
    print()

    # =========================
    # CARREGAR MODELO
    # =========================

    print("Carregando modelo WhisperX...")
    print()

    try:

        model = whisperx.load_model(
            MODELO,
            DEVICE,
            compute_type=COMPUTE_TYPE
        )

    except Exception as erro:

        print()
        print("ERRO ao carregar WhisperX:")
        print(erro)

        return False


    # =========================
    # CRIAR PASTA
    # =========================

    os.makedirs(
        PASTA_TEMPOS,
        exist_ok=True
    )


    # =========================
    # PROCESSAR CENAS
    # =========================

    for numero in range(
        1,
        NUM_CENAS + 1
    ):

        arquivo_audio = os.path.join(
            PASTA_AUDIOS,
            f"cena_{numero}.mp3"
        )

        arquivo_json = os.path.join(
            PASTA_TEMPOS,
            f"cena_{numero}.json"
        )


        print()
        print("==============================")
        print(f"CENA {numero}")
        print("==============================")
        print()


        # =========================
        # VERIFICAR ÁUDIO
        # =========================

        if not os.path.exists(
            arquivo_audio
        ):

            print(
                f"ERRO: áudio não encontrado:"
            )

            print(
                arquivo_audio
            )

            return False


        # =========================
        # CARREGAR ÁUDIO
        # =========================

        print(
            "Carregando áudio..."
        )

        audio = whisperx.load_audio(
            arquivo_audio
        )


        # =========================
        # TRANSCRIÇÃO
        # =========================

        print(
            "Transcrevendo áudio..."
        )

        try:

            resultado = model.transcribe(
                audio,
                batch_size=4,
                language="pt"
            )

        except Exception as erro:

            print()
            print(
                "ERRO durante a transcrição:"
            )

            print(erro)

            return False


        # =========================
        # MODELO DE ALINHAMENTO
        # =========================

        print(
            "Carregando alinhamento..."
        )

        try:

            model_a, metadata = (
                whisperx.load_align_model(
                    language_code=resultado["language"],
                    device=DEVICE
                )
            )

        except Exception as erro:

            print()
            print(
                "ERRO ao carregar "
                "modelo de alinhamento:"
            )

            print(erro)

            return False


        # =========================
        # ALINHAR PALAVRAS
        # =========================

        print(
            "Alinhando palavras..."
        )

        try:

            resultado_alinhado = whisperx.align(
                resultado["segments"],
                model_a,
                metadata,
                audio,
                DEVICE,
                return_char_alignments=False
            )

        except Exception as erro:

            print()
            print(
                "ERRO durante o alinhamento:"
            )

            print(erro)

            return False


        # =========================
        # EXTRAIR PALAVRAS
        # =========================

        palavras = []


        for segmento in (
            resultado_alinhado["segments"]
        ):

            palavras_segmento = segmento.get(
                "words",
                []
            )


            for palavra in palavras_segmento:

                if (
                    "start" in palavra
                    and "end" in palavra
                ):

                    palavras.append(
                        {
                            "palavra":
                                palavra["word"],

                            "inicio":
                                round(
                                    palavra["start"],
                                    3
                                ),

                            "fim":
                                round(
                                    palavra["end"],
                                    3
                                )
                        }
                    )


        # =========================
        # VERIFICAR RESULTADO
        # =========================

        if not palavras:

            print()
            print(
                "ERRO: WhisperX não "
                "encontrou palavras."
            )

            return False


        # =========================
        # SALVAR JSON
        # =========================

        with open(
            arquivo_json,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                palavras,
                arquivo,
                ensure_ascii=False,
                indent=4
            )


        # =========================
        # RESULTADO
        # =========================

        print()

        print(
            f"✓ {len(palavras)} palavras "
            "alinhadas."
        )

        print(
            f"✓ JSON salvo: {arquivo_json}"
        )


    # =========================
    # FINAL
    # =========================

    print()
    print("==============================")
    print("WHISPERX CONCLUÍDO!")
    print("==============================")
    print()

    return True
