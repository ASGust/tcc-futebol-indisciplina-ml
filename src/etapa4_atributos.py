# ENGENHARIA DE ATRIBUTOS
#
# Esta é a primeira parte da Etapa 4.
# Nesta etapa são calculados apenas atributos derivados de cada partida
# individualmente, sem utilizar informações de partidas anteriores.
#
# A Etapa 4 será concluída em uma segunda parte, quando serão adicionadas
# novas funções para calcular janelas deslizantes de desempenho histórico
# de 3 a 7 partidas anteriores.
#
# Entrada:
# dados/processados/base_tratada.csv
#
# Saída:
# dados/processados/base_atributos.csv


import pandas as pd
from pathlib import Path
import numpy as np


# CONFIGURAÇÕES
ARQUIVO_ENTRADA = Path("dados/processados/base_tratada.csv")
ARQUIVO_SAIDA = Path("dados/processados/base_atributos.csv")


# FUNÇÕES AUXILIARES
def calcular_pontos(base):
    """
    Calcula os pontos conquistados pelo mandante e pelo visitante
    em cada partida, de acordo com o resultado.

    Resultado:
    H = vitória do mandante
    D = empate
    A = vitória do visitante

    Retorna:
        DataFrame com as colunas de pontos adicionadas.
    """

    base["pontos_mandante"] = 0
    base["pontos_visitante"] = 0

    base.loc[base["resultado"] == "H", "pontos_mandante"] = 3
    base.loc[base["resultado"] == "H", "pontos_visitante"] = 0

    base.loc[base["resultado"] == "D", "pontos_mandante"] = 1
    base.loc[base["resultado"] == "D", "pontos_visitante"] = 1

    base.loc[base["resultado"] == "A", "pontos_mandante"] = 0
    base.loc[base["resultado"] == "A", "pontos_visitante"] = 3

    return base


def calcular_indices_indisciplina(base):
    """
    Calcula o índice ponderado de indisciplina para mandante
    e visitante.

    Peso utilizado:
    - cartão amarelo = 1
    - cartão vermelho = 2

    Também calcula o índice geral de indisciplina da partida,
    somando os índices do mandante e do visitante.

    Retorna:
        DataFrame com os índices de indisciplina adicionados.
    """

    base["indice_indisciplina_mandante"] = (
        base["amarelos_mandante"] * 1
        + base["vermelhos_mandante"] * 2
    )

    base["indice_indisciplina_visitante"] = (
        base["amarelos_visitante"] * 1
        + base["vermelhos_visitante"] * 2
    )

    base["indice_indisciplina_total"] = (
        base["indice_indisciplina_mandante"]
        + base["indice_indisciplina_visitante"]
    )

    return base


def calcular_disciplina_por_falta(base):
    """
    Calcula a proporção de cartões em relação às faltas
    cometidas por cada equipe.

    Fórmula:
        (cartões amarelos + cartões vermelhos) / faltas

    Quando o número de faltas é zero, podem ocorrer dois casos:
    - 0/0, que gera NaN;
    - valor maior que zero dividido por zero, que gera infinito.

    Nos dois casos, o resultado é definido como zero para evitar
    valores ausentes ou infinitos na base.

    Retorna:
        DataFrame com os atributos de disciplina por falta adicionados.
    """

    cartoes_mandante = (
        base["amarelos_mandante"]
        + base["vermelhos_mandante"]
    )

    cartoes_visitante = (
        base["amarelos_visitante"]
        + base["vermelhos_visitante"]
    )

    base["disciplina_por_falta_mandante"] = (
        cartoes_mandante
        .div(base["faltas_mandante"])
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )

    base["disciplina_por_falta_visitante"] = (
        cartoes_visitante
        .div(base["faltas_visitante"])
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )

    return base


def calcular_eficiencia_finalizacao(base):
    """
    Calcula a eficiência de finalização de cada equipe.

    Fórmula:
        chutes a gol / chutes totais

    Quando o número de chutes totais é zero, podem ocorrer dois casos:
    - 0/0, que gera NaN;
    - valor maior que zero dividido por zero, que gera infinito.

    Nos dois casos, o resultado é definido como zero para evitar
    valores ausentes ou infinitos na base.

    Retorna:
        DataFrame com os atributos de eficiência de finalização.
    """

    base["eficiencia_finalizacao_mandante"] = (
        base["chutes_gol_mandante"]
        .div(base["chutes_mandante"])
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )

    base["eficiencia_finalizacao_visitante"] = (
        base["chutes_gol_visitante"]
        .div(base["chutes_visitante"])
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )

    return base


def calcular_atributos_temporais(base):
    """
    Extrai informações temporais da data da partida.

    São criados:
    - dia_semana: nome do dia da semana em português;
    - mes: número do mês, de 1 a 12.

    Retorna:
        DataFrame com os atributos temporais adicionados.
    """

    dias_semana = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }

    base["dia_semana"] = base["data"].dt.dayofweek.map(dias_semana)
    base["mes"] = base["data"].dt.month

    return base


# FUNÇÃO PRINCIPAL
def calcular_atributos_derivados(base_tratada):
    """
    Calcula os atributos derivados da primeira parte da Etapa 4.

    Os atributos são calculados exclusivamente a partir das
    informações da própria partida. Nenhum atributo utiliza
    partidas anteriores ou posteriores.

    São criados:
    - pontos_mandante
    - pontos_visitante
    - indice_indisciplina_mandante
    - indice_indisciplina_visitante
    - indice_indisciplina_total
    - disciplina_por_falta_mandante
    - disciplina_por_falta_visitante
    - eficiencia_finalizacao_mandante
    - eficiencia_finalizacao_visitante
    - dia_semana
    - mes

    Retorna:
        DataFrame com todas as colunas originais e os novos
        atributos derivados.
    """

    print("\n" + "=" * 70)
    print("ETAPA 4 — ENGENHARIA DE ATRIBUTOS")
    print("PARTE 1 — ATRIBUTOS DERIVADOS")
    print("=" * 70)

    base = base_tratada.copy()

    linhas_antes = len(base)
    colunas_antes = len(base.columns)

    print("\nDimensões antes da engenharia de atributos:")
    print(f"Linhas   : {linhas_antes}")
    print(f"Colunas  : {colunas_antes}")

    # Cálculo dos atributos derivados
    base = calcular_pontos(base)
    base = calcular_indices_indisciplina(base)
    base = calcular_disciplina_por_falta(base)
    base = calcular_eficiencia_finalizacao(base)
    base = calcular_atributos_temporais(base)

    linhas_depois = len(base)
    colunas_depois = len(base.columns)

    print("\nDimensões depois da engenharia de atributos:")
    print(f"Linhas   : {linhas_depois}")
    print(f"Colunas  : {colunas_depois}")

    # Verificação de que o número de linhas foi preservado
    if linhas_antes == linhas_depois:
        print("[OK] O número de linhas foi preservado.")
    else:
        print("[ATENÇÃO] O número de linhas foi alterado.")

    # Verificação das colunas criadas
    colunas_criadas = [
        "pontos_mandante",
        "pontos_visitante",
        "indice_indisciplina_mandante",
        "indice_indisciplina_visitante",
        "indice_indisciplina_total",
        "disciplina_por_falta_mandante",
        "disciplina_por_falta_visitante",
        "eficiencia_finalizacao_mandante",
        "eficiencia_finalizacao_visitante",
        "dia_semana",
        "mes"
    ]

    print("\nColunas criadas:")
    for coluna in colunas_criadas:
        print(f" - {coluna}")

    # Verificação de valores ausentes nas novas colunas
    print("\n" + "-" * 70)
    print("VERIFICAÇÃO DE VALORES AUSENTES NAS COLUNAS CRIADAS")
    print("-" * 70)

    ausencias = base[colunas_criadas].isna().sum()

    encontrou_ausencias = False

    for coluna, quantidade in ausencias.items():
        if quantidade > 0:
            encontrou_ausencias = True
            print(
                f"[ATENÇÃO] {coluna}: "
                f"{quantidade} valor(es) ausente(s)."
            )

    if not encontrou_ausencias:
        print(
            "[OK] Nenhum valor ausente foi introduzido nas "
            "colunas criadas."
        )

    # Verificação de valores infinitos nas novas colunas
    print("\n" + "-" * 70)
    print("VERIFICAÇÃO DE VALORES INFINITOS NAS COLUNAS CRIADAS")
    print("-" * 70)

    infinitos = base[colunas_criadas].isin([np.inf, -np.inf]).sum()

    if infinitos.sum() > 0:
        print("[ATENÇÃO] Foram encontrados valores infinitos:")
        print(infinitos[infinitos > 0])
    else:
        print(
            "[OK] Nenhum valor infinito foi encontrado nas "
            "colunas criadas."
        )

    # Verificação específica da coluna arbitro
    print("\nVerificação da coluna 'arbitro':")

    ausencias_arbitro = base["arbitro"].isna().sum()

    print(
        f"Valores ausentes em arbitro: "
        f"{ausencias_arbitro}"
    )

    print(
        "Observação: as ausências em 'arbitro' já estavam presentes "
        "na base tratada e não são consideradas valores ausentes "
        "introduzidos pela Etapa 4."
    )

    # Primeiras cinco linhas
    print("\n" + "-" * 70)
    print("PRIMEIRAS 5 LINHAS APÓS A ENGENHARIA DE ATRIBUTOS")
    print("-" * 70)

    print(base.head(5).to_string(index=False))

    return base


# PARTE 2 — JANELAS DESLIZANTES DE DESEMPENHO HISTÓRICO
# ATENÇÃO — VAZAMENTO DE DADOS:
# Os 11 atributos criados na Parte 1, assim como as estatísticas
# brutas da partida atual, descrevem acontecimentos DURANTE a
# própria partida.
#
# Esses atributos NÃO devem ser utilizados diretamente como
# variáveis de entrada em modelos preditivos do resultado dessa
# mesma partida, pois isso caracteriza vazamento de dados.
#
# Nesta segunda parte, essas informações são utilizadas apenas
# como matéria-prima para calcular médias históricas de partidas
# ANTERIORES.
#
# As médias históricas calculadas abaixo são construídas com
# .shift(1), garantindo que a partida atual não participe do
# próprio histórico.
#
# Portanto, somente as variáveis históricas produzidas nesta
# Parte 2 são candidatas a variáveis de entrada dos modelos.
#
# Os atributos da Parte 1 também podem ser utilizados em análises
# exploratórias e descritivas do TCC.


def construir_historico_times(base):
    """
    Reorganiza a base de partidas em formato longo.

    Cada partida gera duas observações:
    - uma para o mandante;
    - uma para o visitante.

    Dessa forma, cada linha representa uma atuação de determinado
    time em uma partida, permitindo acompanhar seu histórico geral
    independentemente de ter jogado como mandante ou visitante.

    O histórico é ordenado por time e data.

    IMPORTANTE:
        As estatísticas desta estrutura representam o que aconteceu
        em cada partida. Elas serão utilizadas posteriormente apenas
        para construir médias de partidas anteriores.

    Retorna:
        DataFrame em formato longo com uma linha por time e partida.
    """

    colunas_historico = [
        "data",
        "liga",
        "temporada",
        "time",
        "condicao",
        "pontos",
        "indisciplina",
        "amarelos",
        "vermelhos",
        "faltas",
        "gols_marcados",
        "gols_sofridos",
        "chutes",
        "chutes_gol",
        "escanteios"
    ]

    
    # Histórico dos mandantes
    mandantes = pd.DataFrame({
        "partida_id": base.index,
        "data": base["data"],
        "liga": base["liga"],
        "temporada": base["temporada"],
        "time": base["time_mandante"],
        "condicao": "mandante",
        "pontos": base["pontos_mandante"],
        "indisciplina": base["indice_indisciplina_mandante"],
        "amarelos": base["amarelos_mandante"],
        "vermelhos": base["vermelhos_mandante"],
        "faltas": base["faltas_mandante"],
        "gols_marcados": base["gols_mandante"],
        "gols_sofridos": base["gols_visitante"],
        "chutes": base["chutes_mandante"],
        "chutes_gol": base["chutes_gol_mandante"],
        "escanteios": base["escanteios_mandante"]
    })

    # Histórico dos visitantes
    visitantes = pd.DataFrame({
        "partida_id": base.index,
        "data": base["data"],
        "liga": base["liga"],
        "temporada": base["temporada"],
        "time": base["time_visitante"],
        "condicao": "visitante",
        "pontos": base["pontos_visitante"],
        "indisciplina": base["indice_indisciplina_visitante"],
        "amarelos": base["amarelos_visitante"],
        "vermelhos": base["vermelhos_visitante"],
        "faltas": base["faltas_visitante"],
        "gols_marcados": base["gols_visitante"],
        "gols_sofridos": base["gols_mandante"],
        "chutes": base["chutes_visitante"],
        "chutes_gol": base["chutes_gol_visitante"],
        "escanteios": base["escanteios_visitante"]
    })

    
    # União dos dois lados da partida
    historico_times = pd.concat(
        [mandantes, visitantes],
        ignore_index=True
    )

    # Garante que a data esteja em formato datetime.
    historico_times["data"] = pd.to_datetime(
        historico_times["data"],
        errors="coerce"
    )

    # Ordenação cronológica por time.
    historico_times = historico_times.sort_values(
        ["time", "data", "partida_id"]
    ).reset_index(drop=True)

    return historico_times[
        ["partida_id"] + colunas_historico
    ]


def calcular_medias_moveis(
    historico_times,
    tamanhos_janela=[3, 4, 5, 6, 7]
):
    """
    Calcula médias móveis históricas para cada time.

    Para cada tamanho de janela, são utilizadas somente as
    partidas ANTERIORES à partida atual.

    O uso de shift(1) antes de rolling() é essencial para
    excluir a partida atual do cálculo e evitar vazamento
    de dados.

    São calculadas médias das seguintes estatísticas:
    - pontos
    - indisciplina
    - amarelos
    - vermelhos
    - faltas
    - gols_marcados
    - gols_sofridos
    - chutes
    - chutes_gol
    - escanteios

    É utilizado min_periods igual ao tamanho da janela.
    Portanto, quando o time ainda não possui partidas
    anteriores suficientes, o resultado permanece NaN.

    Retorna:
        DataFrame com as médias históricas adicionadas.
    """

    estatisticas = [
        "pontos",
        "indisciplina",
        "amarelos",
        "vermelhos",
        "faltas",
        "gols_marcados",
        "gols_sofridos",
        "chutes",
        "chutes_gol",
        "escanteios"
    ]

    historico_com_medias = historico_times.copy()

    # Garante a ordenação cronológica antes do cálculo.
    historico_com_medias = historico_com_medias.sort_values(
        ["time", "data", "partida_id"]
    ).reset_index(drop=True)

    
    # Cálculo das janelas
    for tamanho in tamanhos_janela:

        for estatistica in estatisticas:

            nome_coluna = (
                f"{estatistica}_media_ult{tamanho}"
            )

            historico_com_medias[nome_coluna] = (
                historico_com_medias
                .groupby("time")[estatistica]
                .transform(
                    lambda serie: (
                        serie
                        .shift(1)
                        .rolling(
                            window=tamanho,
                            min_periods=tamanho
                        )
                        .mean()
                    )
                )
            )

    return historico_com_medias


def juntar_historico_na_base(
    base,
    historico_com_medias
):
    """
    Junta as médias históricas calculadas de volta à base
    original de partidas.

    As médias são separadas conforme a condição do time
    na partida atual:

    - mandante_* para o time que joga em casa;
    - visitante_* para o time que joga fora.

    A ligação é feita utilizando o identificador da partida
    e a condição do time, garantindo que as médias sejam
    associadas à equipe correta.

    Retorna:
        DataFrame original com as médias históricas adicionadas.
    """

    base_resultado = base.copy()

    estatisticas = [
        "pontos",
        "indisciplina",
        "amarelos",
        "vermelhos",
        "faltas",
        "gols_marcados",
        "gols_sofridos",
        "chutes",
        "chutes_gol",
        "escanteios"
    ]

    tamanhos_janela = [3, 4, 5, 6, 7]

    # Identificador temporário da partida.
    base_resultado["_partida_id"] = base_resultado.index

    
    # Seleciona somente as médias históricas.
    colunas_medias = []

    for tamanho in tamanhos_janela:
        for estatistica in estatisticas:
            colunas_medias.append(
                f"{estatistica}_media_ult{tamanho}"
            )

    colunas_juncao = [
        "partida_id",
        "condicao"
    ] + colunas_medias

    medias = historico_com_medias[colunas_juncao].copy()

    
    # Médias do mandante
    medias_mandante = medias[
        medias["condicao"] == "mandante"
    ].copy()

    medias_mandante = medias_mandante.drop(
        columns="condicao"
    )

    renomear_mandante = {}

    for coluna in colunas_medias:
        renomear_mandante[coluna] = (
            f"mandante_{coluna}"
        )

    medias_mandante = medias_mandante.rename(
        columns=renomear_mandante
    )

    base_resultado = base_resultado.merge(
        medias_mandante,
        left_on="_partida_id",
        right_on="partida_id",
        how="left"
    )

    base_resultado = base_resultado.drop(
        columns="partida_id"
    )

    
    # Médias do visitante
    medias_visitante = medias[
        medias["condicao"] == "visitante"
    ].copy()

    medias_visitante = medias_visitante.drop(
        columns="condicao"
    )

    renomear_visitante = {}

    for coluna in colunas_medias:
        renomear_visitante[coluna] = (
            f"visitante_{coluna}"
        )

    medias_visitante = medias_visitante.rename(
        columns=renomear_visitante
    )

    base_resultado = base_resultado.merge(
        medias_visitante,
        left_on="_partida_id",
        right_on="partida_id",
        how="left"
    )

    base_resultado = base_resultado.drop(
        columns=["partida_id", "_partida_id"]
    )

    return base_resultado


def verificar_vazamento_dados(
    base,
    historico_times,
    quantidade_partidas=3
):
    """
    Verifica, para partidas selecionadas aleatoriamente, se as
    partidas utilizadas no histórico são estritamente anteriores
    à partida atual.

    Para cada partida selecionada, são exibidas as últimas três
    partidas anteriores do mandante e suas respectivas datas.

    A verificação confirma explicitamente que nenhuma partida
    atual ou futura foi utilizada no cálculo histórico.
    """

    print("\n" + "-" * 70)
    print("VERIFICAÇÃO DE AUSÊNCIA DE VAZAMENTO DE DADOS")
    print("-" * 70)

    # Seleção determinística para facilitar a reprodução dos resultados.
    partidas_teste = base.sample(
        n=min(quantidade_partidas, len(base)),
        random_state=42
    )

    for numero, (_, partida) in enumerate(
        partidas_teste.iterrows(),
        start=1
    ):

        data_atual = partida["data"]
        mandante = partida["time_mandante"]

        historico_mandante = historico_times[
            (historico_times["time"] == mandante)
            & (historico_times["data"] < data_atual)
        ].sort_values(
            ["data", "partida_id"],
            ascending=False
        )

        partidas_anteriores = historico_mandante.head(3)

        print(f"\nPartida de teste {numero}:")
        print(
            f"Data atual    : "
            f"{data_atual.strftime('%Y-%m-%d')}"
        )
        print(f"Mandante      : {mandante}")
        print(
            f"Visitante     : "
            f"{partida['time_visitante']}"
        )

        print(
            "\nÚltimas 3 partidas anteriores do mandante "
            "utilizadas como histórico:"
        )

        if len(partidas_anteriores) == 0:
            print("Nenhuma partida anterior disponível.")

        else:
            for _, historico in partidas_anteriores.iterrows():
                print(
                    f" - {historico['data'].strftime('%Y-%m-%d')} "
                    f"| {historico['time']} "
                    f"| {historico['condicao']}"
                )

        if len(partidas_anteriores) > 0:
            todas_anteriores = (
                partidas_anteriores["data"] < data_atual
            ).all()

            if todas_anteriores:
                print(
                    "[OK] Todas as datas utilizadas são "
                    "estritamente anteriores à partida atual."
                )
            else:
                print(
                    "[ATENÇÃO] Foi encontrada uma data que "
                    "não é anterior à partida atual."
                )


def gerar_relatorio_ausencias(
    base,
    tamanhos_janela=[3, 4, 5, 6, 7]
):
    """
    Gera um relatório de valores ausentes nas janelas históricas.

    Para cada tamanho de janela, contabiliza:
    - quantidade de linhas com pelo menos um NaN nas médias
      daquela janela;
    - quantidade de times distintos afetados.

    As linhas não são removidas nem preenchidas.

    Retorna:
        Dicionário com o resumo das ausências por janela.
    """

    estatisticas = [
        "pontos",
        "indisciplina",
        "amarelos",
        "vermelhos",
        "faltas",
        "gols_marcados",
        "gols_sofridos",
        "chutes",
        "chutes_gol",
        "escanteios"
    ]

    relatorio = {}

    print("\n" + "-" * 70)
    print("RELATÓRIO DE AUSÊNCIAS NAS JANELAS HISTÓRICAS")
    print("-" * 70)

    for tamanho in tamanhos_janela:

        colunas_janela = []

        for lado in ["mandante", "visitante"]:
            for estatistica in estatisticas:
                colunas_janela.append(
                    f"{lado}_{estatistica}_media_ult{tamanho}"
                )

        linhas_com_nan = base[colunas_janela].isna().any(
            axis=1
        )

        quantidade_linhas = int(
            linhas_com_nan.sum()
        )

        # Times afetados: verifica separadamente os times
        # mandantes e visitantes nas linhas que possuem NaN.
        times_afetados = set()

        for indice in base.index[linhas_com_nan]:

            times_afetados.add(
                base.loc[indice, "time_mandante"]
            )

            times_afetados.add(
                base.loc[indice, "time_visitante"]
            )

        quantidade_times = len(times_afetados)

        relatorio[tamanho] = {
            "linhas_com_nan": quantidade_linhas,
            "times_distintos_afetados": quantidade_times
        }

        print(
            f"Janela ult{tamanho}: "
            f"{quantidade_linhas} linha(s) com NaN | "
            f"{quantidade_times} time(s) distinto(s) afetado(s)"
        )

    return relatorio


def gerar_categorizacao_colunas(base):
    """
    Categoriza as colunas da base final em quatro grupos:

    1. identificacao
    2. atributos_partida_atual_NAO_USAR_EM_MODELO_PREDITIVO
    3. janelas_disciplinares
    4. janelas_desempenho_estilo

    A categorização é utilizada posteriormente na Etapa 5
    para montar os conjuntos de variáveis dos modelos com
    e sem atributos de indisciplina.

    Retorna:
        Dicionário com as quatro categorias de colunas.
    """

    identificacao = [
        "liga",
        "temporada",
        "data",
        "time_mandante",
        "time_visitante",
        "arbitro",
        "resultado"
    ]

    atributos_parte1 = [
        "pontos_mandante",
        "pontos_visitante",
        "indice_indisciplina_mandante",
        "indice_indisciplina_visitante",
        "indice_indisciplina_total",
        "disciplina_por_falta_mandante",
        "disciplina_por_falta_visitante",
        "eficiencia_finalizacao_mandante",
        "eficiencia_finalizacao_visitante",
        "dia_semana",
        "mes"
    ]

    estatisticas_brutas = [
        "gols_mandante",
        "gols_visitante",
        "chutes_mandante",
        "chutes_visitante",
        "chutes_gol_mandante",
        "chutes_gol_visitante",
        "escanteios_mandante",
        "escanteios_visitante",
        "faltas_mandante",
        "faltas_visitante",
        "amarelos_mandante",
        "amarelos_visitante",
        "vermelhos_mandante",
        "vermelhos_visitante",
        "total_cartoes_amarelos",
        "total_cartoes_vermelhos",
        "total_faltas",
        "total_gols"
    ]

    atributos_atual = (
        atributos_parte1
        + estatisticas_brutas
    )

    janelas_disciplinares = []
    janelas_desempenho_estilo = []

    for coluna in base.columns:

        if "_media_ult" not in coluna:
            continue

        nome_base = coluna

        estatisticas_disciplinares = [
            "indisciplina",
            "amarelos",
            "vermelhos",
            "faltas"
        ]

        estatisticas_desempenho = [
            "pontos",
            "gols_marcados",
            "gols_sofridos",
            "chutes",
            "chutes_gol",
            "escanteios"
        ]

        if any(
            f"_{estatistica}_media_ult" in nome_base
            for estatistica in estatisticas_disciplinares
        ):
            janelas_disciplinares.append(coluna)

        elif any(
            f"_{estatistica}_media_ult" in nome_base
            for estatistica in estatisticas_desempenho
        ):
            janelas_desempenho_estilo.append(coluna)

    categorizacao = {
        "identificacao": identificacao,
        "atributos_partida_atual_NAO_USAR_EM_MODELO_PREDITIVO":
            atributos_atual,
        "janelas_disciplinares":
            sorted(janelas_disciplinares),
        "janelas_desempenho_estilo":
            sorted(janelas_desempenho_estilo)
    }

    return categorizacao


def salvar_categorizacao_colunas(categorizacao):
    """
    Salva a categorização das colunas em formato JSON.

    Retorna:
        Caminho do arquivo salvo.
    """

    caminho = Path(
        "resultados/tabelas/categorizacao_colunas.json"
    )

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    import json

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            categorizacao,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    return caminho


def calcular_janelas_deslizantes(base_com_atributos):
    """
    Calcula as janelas deslizantes de desempenho histórico.

    Esta função representa a segunda parte da Etapa 4.

    IMPORTANTE — VAZAMENTO DE DADOS:
        Os atributos da Parte 1 e as estatísticas brutas da
        partida atual descrevem acontecimentos que somente podem
        ser conhecidos durante ou depois da partida.

        Portanto, eles NÃO devem ser utilizados diretamente como
        variáveis de entrada em modelos preditivos para o resultado
        da própria partida.

        Nesta função, essas informações são utilizadas somente
        como matéria-prima para construir médias de partidas
        anteriores. O uso de shift(1) antes de rolling() garante
        que a partida atual seja excluída das janelas históricas.

        As médias históricas produzidas nesta função são as
        variáveis candidatas para utilização nos modelos.

    Etapas realizadas:
    1. Construção do histórico dos times em formato longo;
    2. Cálculo das médias móveis de 3 a 7 partidas anteriores;
    3. Retorno das médias para a base original;
    4. Verificação de ausência de vazamento;
    5. Relatório de valores ausentes;
    6. Categorização das colunas.

    Retorna:
        DataFrame final com os atributos da Parte 1 e as
        janelas históricas adicionadas.
    """

    print("\n" + "=" * 70)
    print("ETAPA 4 — PARTE 2")
    print("JANELAS DESLIZANTES DE DESEMPENHO HISTÓRICO")
    print("=" * 70)


    # 1. Construção do histórico longo
    historico_times = construir_historico_times(
        base_com_atributos
    )

    print("\n[OK] Histórico dos times construído.")
    print(
        f"Linhas no histórico longo: "
        f"{len(historico_times)}"
    )

    # Cada partida gera duas linhas no histórico.
    if len(historico_times) == len(base_com_atributos) * 2:
        print(
            "[OK] Cada partida gerou duas observações "
            "no histórico."
        )
    else:
        print(
            "[ATENÇÃO] O histórico não possui exatamente "
            "duas observações por partida."
        )

    # 2. Cálculo das médias móveis
    historico_com_medias = calcular_medias_moveis(
        historico_times,
        tamanhos_janela=[3, 4, 5, 6, 7]
    )

    print(
        "[OK] Médias históricas de 3 a 7 partidas "
        "calculadas."
    )

   
    # 3. Retorno das médias para a base original
    base_final = juntar_historico_na_base(
        base_com_atributos,
        historico_com_medias
    )

    print(
        "[OK] Médias históricas incorporadas à base "
        "original."
    )

  
    # 4. Verificação de vazamento
    verificar_vazamento_dados(
        base_com_atributos,
        historico_times,
        quantidade_partidas=3
    )

    
    # 5. Relatório de ausências
    relatorio_ausencias = gerar_relatorio_ausencias(
        base_final,
        tamanhos_janela=[3, 4, 5, 6, 7]
    )

    
    # 6. Categorização das colunas
    categorizacao = gerar_categorizacao_colunas(
        base_final
    )

    caminho_categorizacao = salvar_categorizacao_colunas(
        categorizacao
    )

    print(
        f"\n[OK] Categorização das colunas salva em: "
        f"{caminho_categorizacao}"
    )

    
    # 7. Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DAS JANELAS HISTÓRICAS")
    print("=" * 70)

    for tamanho, dados in relatorio_ausencias.items():
        print(
            f"ult{tamanho}: "
            f"{dados['linhas_com_nan']} linha(s) com NaN | "
            f"{dados['times_distintos_afetados']} time(s) afetado(s)"
        )

    return base_final


# EXECUÇÃO COMPLETA DA ETAPA 4
if __name__ == "__main__":

    print("\nCarregando base tratada...")

    if not ARQUIVO_ENTRADA.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {ARQUIVO_ENTRADA}"
        )

    base_tratada = pd.read_csv(
        ARQUIVO_ENTRADA,
        encoding="utf-8-sig"
    )

    # Garante que a coluna de data seja reconhecida como datetime.
    base_tratada["data"] = pd.to_datetime(
        base_tratada["data"],
        errors="coerce"
    )

    # PARTE 1 — ATRIBUTOS DERIVADOS
    base_com_atributos = calcular_atributos_derivados(
        base_tratada
    )

    
    # PARTE 2 — JANELAS DESLIZANTES
    base_atributos = calcular_janelas_deslizantes(
        base_com_atributos
    )

    # SALVAMENTO DA BASE FINAL
    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    base_atributos.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )

   
    # NOVAS COLUNAS DA PARTE 2
    colunas_parte2 = [
        coluna
        for coluna in base_atributos.columns
        if "_media_ult" in coluna
    ]

    print("\n" + "=" * 70)
    print("NOVAS COLUNAS — PARTE 2")
    print("=" * 70)

    print(
        f"Quantidade de novas colunas de janelas: "
        f"{len(colunas_parte2)}"
    )

    for coluna in colunas_parte2:
        print(f" - {coluna}")

    
    # DIMENSÕES FINAIS
    print("\n" + "=" * 70)
    print("ETAPA 4 — CONCLUÍDA")
    print("=" * 70)

    print(
        f"Dimensões finais da base: "
        f"{len(base_atributos)} linhas x "
        f"{len(base_atributos.columns)} colunas"
    )

    print(
        f"\nArquivo final salvo em: "
        f"{ARQUIVO_SAIDA}"
    )

    print(
        "\n[OK] Arquivo de categorização salvo em:"
        "\nresultados/tabelas/categorizacao_colunas.json"
    )

    print("=" * 70)