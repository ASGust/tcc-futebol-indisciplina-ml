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


# EXECUÇÃO DA ETAPA
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

    base_atributos = calcular_atributos_derivados(
        base_tratada
    )

    # Salvamento da base resultante
    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    base_atributos.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 70)
    print("ETAPA 4 — PARTE 1 CONCLUÍDA")
    print("=" * 70)
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")
    print(f"Linhas finais  : {len(base_atributos)}")
    print(f"Colunas finais : {len(base_atributos.columns)}")
    print("=" * 70)