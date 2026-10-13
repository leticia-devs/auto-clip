import requests
import os
import re


def limpar_busca(visual):

    # =========================
    # 1. Limpar texto
    # =========================

    busca = visual.strip()

    # Remove pontuação
    busca = re.sub(r'[^\w\sÀ-ÿ]', ' ', busca)

    # Remove espaços duplicados
    busca = re.sub(r'\s+', ' ', busca)

    # =========================
    # 2. Remover palavras
    #    pouco úteis para busca
    # =========================

    palavras_remover = [
        "uma",
        "um",
        "de",
        "da",
        "do",
        "das",
        "dos",
        "e",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "com",
        "que",
        "para",
        "mostrando",
        "mostra",
        "enquanto",
        "cena",
        "imagem",
        "imagens",
        "plano",
        "geral",
        "plano fechado",
        "vista",
        "fotografia",
        "fotográfico",
        "fotográfica",
    ]

    palavras = busca.split()

    palavras_filtradas = []

    for palavra in palavras:

        if palavra.lower() not in palavras_remover:

            palavras_filtradas.append(palavra)


    busca = " ".join(palavras_filtradas)


    # =========================
    # 3. Limitar tamanho
    # =========================

    palavras = busca.split()

    if len(palavras) > 10:

        palavras = palavras[:10]

    busca = " ".join(palavras)


    return busca


def buscar_visuais(roteiro):

    # =========================
    # 1. Extrair visuais
    # =========================

    linhas = roteiro.splitlines()

    visuais = []

    for linha in linhas:

        linha = linha.strip()

        if "VISUAL:" in linha.upper():

            visual = linha.split(":", 1)[1].strip()

            if visual:

                visuais.append(visual)


    # =========================
    # 2. Verificar
    # =========================

    if not visuais:

        print("\nERRO: nenhum visual foi encontrado no roteiro.")

        return False


    print("\n========== VISUAIS ==========\n")

    for numero, visual in enumerate(visuais, 1):

        print(f"CENA {numero}:")
        print(visual)

        busca = limpar_busca(visual)

        print(f"BUSCA PEXELS: {busca}")
        print()


    # =========================
    # 3. Configurar Pexels
    # =========================

    API_KEY = os.getenv("PEXELS_API_KEY")

    if not API_KEY:

        print("\nERRO: PEXELS_API_KEY não encontrada.")

        return False


    pasta = "visuais"

    os.makedirs(pasta, exist_ok=True)


    # =========================
    # 4. Apagar imagens antigas
    # =========================

    for arquivo in os.listdir(pasta):

        if (
            arquivo.startswith("cena_")
            and arquivo.endswith(".jpg")
        ):

            os.remove(
                os.path.join(pasta, arquivo)
            )


    headers = {
        "Authorization": API_KEY
    }

    url = "https://api.pexels.com/v1/search"


    # =========================
    # 5. Buscar imagens
    # =========================

    print("\n========== BUSCANDO IMAGENS ==========\n")

    imagens_criadas = 0


    for numero, visual in enumerate(visuais, 1):

        print(f"Pesquisando CENA {numero}...")


        # =========================
        # Criar busca
        # =========================

        busca = limpar_busca(visual)

        print(f"Busca Pexels: {busca}")


        params = {
            "query": busca,
            "per_page": 10,
            "orientation": "portrait"
        }


        # =========================
        # Fazer pesquisa
        # =========================

        try:

            resposta = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

        except requests.RequestException as erro:

            print(
                f"Erro de conexão: {erro}"
            )

            continue


        if resposta.status_code != 200:

            print(
                f"Erro na API: "
                f"{resposta.status_code}"
            )

            continue


        # =========================
        # Ler resultado
        # =========================

        try:

            dados = resposta.json()

        except ValueError:

            print("Erro ao interpretar resposta da API.")

            continue


        fotos = dados.get(
            "photos",
            []
        )


        if not fotos:

            print(
                "Nenhuma imagem encontrada."
            )

            continue


        print(
            f"{len(fotos)} imagens encontradas."
        )


        # =========================
        # Escolher imagem
        # =========================

        foto = fotos[0]


        # =========================
        # URL da imagem
        # =========================

        imagem_url = foto["src"]["large2x"]


        print("Baixando imagem...")


        # =========================
        # Baixar imagem
        # =========================

        try:

            imagem = requests.get(
                imagem_url,
                timeout=30
            )

        except requests.RequestException as erro:

            print(
                f"Erro ao baixar imagem: "
                f"{erro}"
            )

            continue


        if imagem.status_code != 200:

            print(
                "Erro ao baixar imagem."
            )

            continue


        # =========================
        # Salvar
        # =========================

        arquivo = os.path.join(
            pasta,
            f"cena_{numero}.jpg"
        )


        with open(
            arquivo,
            "wb"
        ) as f:

            f.write(
                imagem.content
            )


        print(
            f"Imagem salva: {arquivo}"
        )

        print()

        imagens_criadas += 1


    # =========================
    # 6. Resultado
    # =========================

    print("==============================")
    print("VISUAIS CONCLUÍDOS!")
    print("==============================")


    print(
        f"{imagens_criadas} de "
        f"{len(visuais)} imagens foram criadas."
    )


    return (
        imagens_criadas
        == len(visuais)
    )