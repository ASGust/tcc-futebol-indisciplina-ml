# DOWNLOAD DOS DADOS
import requests
from pathlib import Path


# CONFIGURAÇÕES
# Ligas que serão utilizadas no TCC

#Dicionario(sugestão)
# LG = {
#     'E0': "Premier League",
#     'SP1': "La Liga",
#     'I1': "Serie A",
#     'D1': "Bundesliga",
#     'F1': "Ligue 1"
# }
LIGAS = [
    "E0",   # Premier League
    "SP1",  # La Liga
    "I1",   # Serie A
    "D1",   # Bundesliga
    "F1"    # Ligue 1
]

# Temporadas de 2015/2016 até 2024/2025
TEMPORADAS = [
    "1516",
    "1617",
    "1718",
    "1819",
    "1920",
    "2021",
    "2122",
    "2223",
    "2324",
    "2425"
]

# URL base dos arquivos
URL_BASE = "https://www.football-data.co.uk/mmz4281"

# Pasta onde os arquivos originais serão armazenados
PASTA_DADOS_BRUTOS = Path("dados/brutos")


# PROGRAMA PRINCIPAL
def baixar_todos_os_arquivos():
    """
    Baixa todos os arquivos CSV de LIGAS x TEMPORADAS, pulando
    os que já existem em disco (cache).

    Devolve um dicionário com o resumo do download, para que o
    main.py do projeto possa decidir se continua para a próxima
    etapa (por exemplo, não seguir adiante se tudo falhou).
    """

    # PREPARAÇÃO DA PASTA
    PASTA_DADOS_BRUTOS.mkdir(parents=True, exist_ok=True)

    # CONTADORES
    quantidade_baixados = 0
    quantidade_cache = 0
    quantidade_falhas = 0

    # DOWNLOAD DOS ARQUIVOS
    for temporada in TEMPORADAS:

        for liga in LIGAS:

            nome_arquivo = f"{liga}_{temporada}.csv"
            caminho_arquivo = PASTA_DADOS_BRUTOS / nome_arquivo

            # VERIFICAÇÃO DO CACHE
            if caminho_arquivo.exists():
                print(f"[CACHE] {nome_arquivo} já existe.")
                quantidade_cache += 1
                continue

            # MONTAGEM DA URL
            url = f"{URL_BASE}/{temporada}/{liga}.csv"

            print(f"[DOWNLOAD] Baixando {nome_arquivo}...")

            try:

                resposta = requests.get(url, timeout=30)

                # Gera erro caso o servidor retorne, por exemplo,
                # código 404 ou 500.
                resposta.raise_for_status()

                # Verifica se foi retornado algum conteúdo.
                if not resposta.content:
                    raise ValueError("O arquivo retornado está vazio.")

                # Salva o arquivo na pasta de dados brutos.
                with open(caminho_arquivo, "wb") as arquivo:
                    arquivo.write(resposta.content)

                print(f"[OK] {nome_arquivo} baixado com sucesso.")
                quantidade_baixados += 1

            except requests.exceptions.RequestException as erro:

                print(f"[ERRO] Falha ao baixar {nome_arquivo}: {erro}")
                quantidade_falhas += 1

            except Exception as erro:

                print(f"[ERRO] Problema ao salvar {nome_arquivo}: {erro}")
                quantidade_falhas += 1

    # RESUMO FINAL
    print("\n" + "=" * 60)
    print("RESUMO DO DOWNLOAD")
    print("=" * 60)

    print(f"Arquivos baixados agora : {quantidade_baixados}")
    print(f"Arquivos já em cache    : {quantidade_cache}")
    print(f"Arquivos com falha      : {quantidade_falhas}")
    print("=" * 60)

    # Devolve o resumo para quem chamou esta função.
    return {
        "baixados": quantidade_baixados,
        "cache": quantidade_cache,
        "falhas": quantidade_falhas
    }


# EXECUTAR O PROGRAMA
if __name__ == "__main__":
    baixar_todos_os_arquivos()