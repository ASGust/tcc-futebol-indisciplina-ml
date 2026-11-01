#UNIFICAÇÃO DOS DADOS
import pandas as pd
from pathlib import Path


#CONFIGURAÇÕES
# Pasta onde estão os arquivos CSV baixados na etapa de download
PASTA_DADOS_BRUTOS = Path("dados/brutos")

# Pasta onde será salva a base unificada
PASTA_DADOS_PROCESSADOS = Path("dados/processados")

# Nome do arquivo final
ARQUIVO_SAIDA = "base_unificada.csv"



# COLUNAS PERMITIDAS (WHITELIST)
# Somente estas colunas serão utilizadas.
COLUNAS_PERMITIDAS = [
    "Date",
    "Referee",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "HS",
    "AS",
    "HST",
    "AST",
    "HC",
    "AC",
    "HF",
    "AF",
    "HY",
    "AY",
    "HR",
    "AR"
]



#RENOMEAÇÃO DAS COLUNAS
RENOMEAR_COLUNAS = {
    "Date": "data",
    "Referee": "arbitro",
    "HomeTeam": "time_mandante",
    "AwayTeam": "time_visitante",

    "FTHG": "gols_mandante",
    "FTAG": "gols_visitante",
    "FTR": "resultado",

    "HS": "chutes_mandante",
    "AS": "chutes_visitante",

    "HST": "chutes_gol_mandante",
    "AST": "chutes_gol_visitante",

    "HC": "escanteios_mandante",
    "AC": "escanteios_visitante",

    "HF": "faltas_mandante",
    "AF": "faltas_visitante",

    "HY": "amarelos_mandante",
    "AY": "amarelos_visitante",

    "HR": "vermelhos_mandante",
    "AR": "vermelhos_visitante"
}


#CONVERTER CÓDIGO DA TEMPORADA
def converter_temporada(codigo):
    """
    Converte o código da temporada para o formato AAAA/AAAA.

    Exemplos:
    1516 -> 2015/2016
    1920 -> 2019/2020
    2021 -> 2020/2021
    2324 -> 2023/2024
    """

    # A temporada 2020/2021 possui este código específico.
    if codigo == "2021":
        return "2020/2021"

    ano_inicio = 2000 + int(codigo[:2])
    ano_fim = 2000 + int(codigo[2:])

    return f"{ano_inicio}/{ano_fim}"


# VERIFICAR TODOS OS CABEÇALHOS DOS ARQUIVOS
def verificar_cabecalhos(arquivos):
    """
    Lê somente os cabeçalhos dos arquivos CSV e retorna
    a união de todas as colunas encontradas.

    Isso serve para inspecionar, antes de processar qualquer
    dado, quais colunas realmente existem nos arquivos brutos
    (por exemplo, para confirmar que não há colunas de posse
    de bola ou passes).
    """

    todas_as_colunas = set()

    for arquivo in arquivos:

        try:

            cabecalho = pd.read_csv(
                arquivo,
                encoding="latin-1",
                nrows=0
            )

            for coluna in cabecalho.columns:
                todas_as_colunas.add(coluna.strip())

        except Exception as erro:

            print(
                f"[ERRO] Não foi possível ler o cabeçalho "
                f"de {arquivo.name}: {erro}"
            )

    return sorted(todas_as_colunas)


#VERIFICAR POSSE DE BOLA E PASSES
def verificar_posse_e_passes(colunas):
    """
    Procura nos cabeçalhos encontrados palavras relacionadas
    a posse de bola e passes.
    """

    colunas_posse = []
    colunas_passes = []

    for coluna in colunas:

        nome = coluna.lower()

        if "possession" in nome or "poss" in nome:
            colunas_posse.append(coluna)

        if "pass" in nome:
            colunas_passes.append(coluna)

    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DE POSSE DE BOLA E PASSES")
    print("=" * 60)

    if colunas_posse:
        print("Possíveis colunas de posse:")
        for coluna in colunas_posse:
            print(f"  - {coluna}")
    else:
        print("Nenhuma coluna de posse de bola encontrada.")

    if colunas_passes:
        print("\nPossíveis colunas de passes:")
        for coluna in colunas_passes:
            print(f"  - {coluna}")
    else:
        print("Nenhuma coluna de passes encontrada.")


# LER UM ARQUIVO CSV
def ler_arquivo(arquivo):
    """
    Lê um CSV utilizando somente as colunas permitidas.

    Se alguma coluna permitida não existir no arquivo,
    ela será criada com valores ausentes (NaN).
    """

    # Primeiro verificamos quais colunas existem no arquivo.
    cabecalho = pd.read_csv(
        arquivo,
        encoding="latin-1",
        nrows=0
    )

    # Limpa espaços em branco tanto do cabeçalho real quanto
    # da whitelist, para a comparação não falhar por causa de
    # um espaço a mais em algum arquivo específico.
    colunas_existentes = [
        coluna.strip()
        for coluna in cabecalho.columns
    ]

    colunas_permitidas_limpas = [
        coluna.strip()
        for coluna in COLUNAS_PERMITIDAS
    ]

    # Seleciona somente as colunas da whitelist que existem.
    colunas_para_ler = [
        coluna
        for coluna in colunas_permitidas_limpas
        if coluna in colunas_existentes
    ]

    # Lê somente as colunas permitidas.
    tabela = pd.read_csv(
        arquivo,
        encoding="latin-1",
        usecols=colunas_para_ler
    )

    # Também limpa os nomes de coluna já lidos, para o restante
    # do código (renomeação, criação de totais etc.) funcionar
    # mesmo que o arquivo original tenha espaços nos cabeçalhos.
    tabela.columns = [
        coluna.strip()
        for coluna in tabela.columns
    ]

    # Se alguma coluna permitida não existir,
    # cria a coluna com valores ausentes.
    for coluna in colunas_permitidas_limpas:

        if coluna not in tabela.columns:
            tabela[coluna] = pd.NA

    # Mantém todas as colunas na mesma ordem.
    tabela = tabela[colunas_permitidas_limpas]

    return tabela


# ADICIONAR LIGA E TEMPORADA
def adicionar_liga_temporada(tabela, arquivo):
    """
    Obtém a liga e a temporada a partir do nome do arquivo.

    Exemplo:
    E0_2324.csv -> liga = E0
                   temporada = 2023/2024
    """

    nome = arquivo.stem

    partes = nome.split("_")

    liga = partes[0]
    codigo_temporada = partes[1]

    temporada = converter_temporada(codigo_temporada)

    tabela["liga"] = liga
    tabela["temporada"] = temporada

    return tabela


# RENOMEAR COLUNAS
def renomear_colunas(tabela):

    tabela = tabela.rename(
        columns=RENOMEAR_COLUNAS
    )

    return tabela


# CRIAR TOTAIS DA PARTIDA
def criar_totais(tabela):
    """
    Cria os totais de:
    - cartões amarelos
    - cartões vermelhos
    - faltas
    - gols

    Se algum dos dois valores utilizados no cálculo estiver
    ausente, o total também será considerado ausente.
    """

    tabela["total_cartoes_amarelos"] = (
        tabela[
            [
                "amarelos_mandante",
                "amarelos_visitante"
            ]
        ].sum(axis=1, min_count=2)
    )

    tabela["total_cartoes_vermelhos"] = (
        tabela[
            [
                "vermelhos_mandante",
                "vermelhos_visitante"
            ]
        ].sum(axis=1, min_count=2)
    )

    tabela["total_faltas"] = (
        tabela[
            [
                "faltas_mandante",
                "faltas_visitante"
            ]
        ].sum(axis=1, min_count=2)
    )

    tabela["total_gols"] = (
        tabela[
            [
                "gols_mandante",
                "gols_visitante"
            ]
        ].sum(axis=1, min_count=2)
    )

    return tabela


# PADRONIZAR A DATA
def padronizar_data(tabela):

    tabela["data"] = pd.to_datetime(
        tabela["data"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    return tabela


#PROGRAMA PRINCIPAL
def unificar_arquivos():
    """
    Executa a Etapa 2 completa: lê os CSVs brutos, monta a
    tabela unificada, salva em disco e devolve o DataFrame
    resultante, para que outros scripts (como o main.py do
    projeto) possam usá-lo sem precisar reler o arquivo salvo.
    """

    print("=" * 60)
    print("ETAPA 2 - CONSTRUÇÃO DA TABELA UNIFICADA")
    print("=" * 60)

    # Criar pasta de saída
    PASTA_DADOS_PROCESSADOS.mkdir(
        parents=True,
        exist_ok=True
    )


    #Encontrar os arquivos CSV
    arquivos = sorted(
        PASTA_DADOS_BRUTOS.glob("*.csv")
    )

    if not arquivos:

        print(
            "\n[ERRO] Nenhum arquivo CSV foi encontrado em:"
        )

        print(PASTA_DADOS_BRUTOS)

        return


    print(
        f"\nArquivos encontrados: {len(arquivos)}"
    )


    #Verificar todos os cabeçalhos
    todas_as_colunas = verificar_cabecalhos(
        arquivos
    )


    print("\n" + "=" * 60)
    print("TODAS AS COLUNAS ENCONTRADAS")
    print("=" * 60)

    for coluna in todas_as_colunas:
        print(coluna)


    # Verificar posse e passes
    verificar_posse_e_passes(
        todas_as_colunas
    )


    #Ler e preparar cada arquivo
    tabelas = []

    for arquivo in arquivos:

        print(
            f"\nProcessando: {arquivo.name}"
        )

        try:

            tabela = ler_arquivo(
                arquivo
            )

            tabela = adicionar_liga_temporada(
                tabela,
                arquivo
            )

            tabela = renomear_colunas(
                tabela
            )

            tabela = criar_totais(
                tabela
            )

            tabelas.append(tabela)

            print(
                f"  Partidas carregadas: {len(tabela)}"
            )

        except Exception as erro:

            print(
                f"  [ERRO] Não foi possível processar "
                f"{arquivo.name}: {erro}"
            )


    #Verificar se algum arquivo foi carregado
    if not tabelas:

        print(
            "\n[ERRO] Nenhum arquivo pôde ser processado."
        )

        return


    #Juntar todos os arquivos
    base_unificada = pd.concat(
        tabelas,
        ignore_index=True
    )


    #Converter data para datetime
    base_unificada = padronizar_data(
        base_unificada
    )


    # Ordenar por data
    base_unificada = base_unificada.sort_values(
        by="data"
    )

    base_unificada = base_unificada.reset_index(
        drop=True
    )


    # Organizar as colunas
    colunas_iniciais = [
        "liga",
        "temporada",
        "data"
    ]

    outras_colunas = [
        coluna
        for coluna in base_unificada.columns
        if coluna not in colunas_iniciais
    ]

    base_unificada = base_unificada[
        colunas_iniciais + outras_colunas
    ]


    # Salvar a base
    caminho_saida = (
        PASTA_DADOS_PROCESSADOS
        / ARQUIVO_SAIDA
    )

    base_unificada.to_csv(
        caminho_saida,
        index=False,
        encoding="utf-8-sig"
    )


    # RESULTADO FINAL
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)

    print(
        f"\nNúmero de linhas: "
        f"{base_unificada.shape[0]}"
    )

    print(
        f"Número de colunas: "
        f"{base_unificada.shape[1]}"
    )


    print("\nPrimeiras 5 linhas:")
    print(
        base_unificada.head(5).to_string(
            index=False
        )
    )


    print("\nValores ausentes por coluna:")
    print(
        base_unificada.isna().sum()
    )


    print("\nBase salva em:")
    print(caminho_saida)

    # Devolve a base para quem chamou esta função.
    return base_unificada


# EXECUTAR O PROGRAMA
if __name__ == "__main__":
    unificar_arquivos()