# SELEÇÃO FINAL DE COLUNAS
#
# Etapa 5 do pipeline.
# Reduz as 136 colunas da base de atributos ao conjunto definido
# para a modelagem: colunas de identificação/controle, atributos
# de data conhecidos antes do jogo e as 100 janelas deslizantes.
#
# Nenhuma linha é removida. Os NaN das janelas (primeiras partidas
# de cada time) são mantidos de propósito: o tratamento fica para a
# etapa de experimentos, quando um tamanho de janela for escolhido.
#
# Entrada:
# dados/processados/base_atributos.csv
#
# Saída:
# dados/processados/base_final.csv


import pandas as pd
from pathlib import Path


# CONFIGURAÇÕES
ARQUIVO_ENTRADA = Path("dados/processados/base_atributos.csv")
ARQUIVO_SAIDA = Path("dados/processados/base_final.csv")


# COLUNAS DE IDENTIFICAÇÃO E CONTROLE
# Inclui o alvo (resultado) e os atributos de data (dia_semana
# e mes), que são conhecidos antes da partida.
COLUNAS_IDENTIFICACAO = [
    "liga",
    "temporada",
    "data",
    "time_mandante",
    "time_visitante",
    "resultado",
    "dia_semana",
    "mes"
]


# COMPOSIÇÃO DAS JANELAS DESLIZANTES
# Padrão dos nomes: <lado>_<estatística>_media_ult<N>
LADOS = ["mandante", "visitante"]

ESTATISTICAS_JANELA = [
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

TAMANHOS_JANELA = [3, 4, 5, 6, 7]


# FUNÇÕES AUXILIARES
def listar_colunas_janela():
    """
    Monta a lista das 100 colunas de janelas deslizantes, na
    mesma ordem em que aparecem na base de atributos (lado,
    depois tamanho da janela, depois estatística).

    Retorna:
        Lista com os nomes das colunas de janela.
    """

    colunas_janela = []

    for lado in LADOS:
        for tamanho in TAMANHOS_JANELA:
            for estatistica in ESTATISTICAS_JANELA:
                colunas_janela.append(
                    f"{lado}_{estatistica}_media_ult{tamanho}"
                )

    return colunas_janela


def verificar_colunas_presentes(base, colunas):
    """
    Confere se todas as colunas esperadas existem na base.
    Interrompe com erro caso alguma esteja faltando, para não
    gerar uma base final incompleta sem aviso.
    """

    colunas_faltantes = [
        coluna
        for coluna in colunas
        if coluna not in base.columns
    ]

    if colunas_faltantes:
        raise KeyError(
            f"Colunas esperadas ausentes na base de atributos: "
            f"{colunas_faltantes}"
        )


def gerar_relatorio_nan_janelas(base, colunas_janela):
    """
    Imprime a quantidade de NaN em cada coluna de janela e, ao
    final, o total de linhas com pelo menos um NaN por tamanho
    de janela.

    As linhas não são removidas nem preenchidas.

    Retorna:
        Série com a quantidade de NaN por coluna de janela.
    """

    nan_por_coluna = base[colunas_janela].isna().sum()

    print("\n" + "-" * 70)
    print("VALORES AUSENTES (NaN) POR COLUNA DE JANELA")
    print("-" * 70)

    for coluna, quantidade in nan_por_coluna.items():
        print(f"{coluna:<40} {quantidade:>5}")

    # Resumo por tamanho de janela
    print("\n" + "-" * 70)
    print("LINHAS COM NaN POR TAMANHO DE JANELA")
    print("-" * 70)

    for tamanho in TAMANHOS_JANELA:

        colunas_tamanho = [
            coluna
            for coluna in colunas_janela
            if coluna.endswith(f"_media_ult{tamanho}")
        ]

        linhas_com_nan = int(
            base[colunas_tamanho].isna().any(axis=1).sum()
        )

        print(
            f"Janela ult{tamanho}: "
            f"{linhas_com_nan} linha(s) com NaN"
        )

    return nan_por_coluna


# PROGRAMA PRINCIPAL
def gerar_base_final(base_atributos):
    """
    Executa a Etapa 5: seleciona as colunas da base final para
    modelagem, salva em disco e devolve o DataFrame resultante,
    para permitir o encadeamento pelo main.py.
    """

    print("=" * 70)
    print("ETAPA 5 - SELEÇÃO FINAL DE COLUNAS")
    print("=" * 70)

    colunas_janela = listar_colunas_janela()
    colunas_finais = COLUNAS_IDENTIFICACAO + colunas_janela

    verificar_colunas_presentes(base_atributos, colunas_finais)

    # Seleção das colunas, na ordem definida
    base_final = base_atributos[colunas_finais].copy()

    # Conferência de que nenhuma linha foi removida
    if len(base_final) != len(base_atributos):
        print("[ATENÇÃO] O número de linhas foi alterado.")

    # Colunas mantidas
    print(
        f"\nColunas mantidas ({len(colunas_finais)}):"
    )

    for posicao, coluna in enumerate(colunas_finais, start=1):
        print(f"{posicao:>3}. {coluna}")

    # Relatório de NaN nas janelas
    gerar_relatorio_nan_janelas(base_final, colunas_janela)

    # Salvar base final
    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    base_final.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 70)
    print("ETAPA 5 CONCLUÍDA")
    print("=" * 70)

    print(
        f"Dimensões finais da base: "
        f"{len(base_final)} linhas x "
        f"{len(base_final.columns)} colunas"
    )

    print(f"Base final salva em: {ARQUIVO_SAIDA}")

    return base_final


# EXECUTAR A ETAPA SOZINHA
if __name__ == "__main__":

    if not ARQUIVO_ENTRADA.exists():

        print(
            f"[ERRO] Arquivo de entrada não encontrado: "
            f"{ARQUIVO_ENTRADA}"
        )

    else:

        base_atributos = pd.read_csv(
            ARQUIVO_ENTRADA,
            encoding="utf-8-sig"
        )

        gerar_base_final(
            base_atributos
        )
