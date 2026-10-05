# ANÁLISE DE DISPONIBILIDADE DOS DADOS

import pandas as pd
from pathlib import Path


# CONFIGURAÇÕES
# Arquivo de entrada gerado na Etapa 2
ARQUIVO_ENTRADA = Path("dados/processados/base_unificada.csv")

# Arquivo de saída da Etapa 3
ARQUIVO_SAIDA = Path("dados/processados/base_tratada.csv")

# Relatório textual da disponibilidade
ARQUIVO_RELATORIO = Path("resultados/tabelas/relatorio_disponibilidade.txt")


# COLUNAS ESTATÍSTICAS PRINCIPAIS
COLUNAS_ESTATISTICAS = [
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
    "gols_mandante",
    "gols_visitante"
]


# REMOVER LINHAS FANTASMA
def remover_linhas_vazias(base_unificada):
    """
    Remove as linhas identificadas como registros fantasma.

    Nesta etapa, uma linha com gols_mandante ausente é utilizada
    como critério para identificar as linhas totalmente vazias
    observadas nos arquivos brutos.
    """

    linhas_antes = len(base_unificada)

    base_tratada = base_unificada[
        base_unificada["gols_mandante"].notna()
    ].copy()

    linhas_removidas = linhas_antes - len(base_tratada)

    print("\n" + "=" * 60)
    print("REMOÇÃO DAS LINHAS FANTASMA")
    print("=" * 60)

    print(f"Linhas antes da limpeza : {linhas_antes}")
    print(f"Linhas removidas        : {linhas_removidas}")
    print(f"Linhas depois da limpeza: {len(base_tratada)}")

    return base_tratada, linhas_removidas


# GERAR RELATÓRIO DE DISPONIBILIDADE
def gerar_relatorio_disponibilidade(base, momento):
    """
    Calcula a quantidade e o percentual de valores ausentes
    para cada coluna da base.

    O parâmetro momento identifica se o relatório corresponde
    ao estado antes ou depois da remoção das linhas fantasma.
    """

    total_linhas = len(base)

    relatorio = pd.DataFrame({
        "coluna": base.columns,
        "ausentes": base.isna().sum().values
    })

    if total_linhas > 0:
        relatorio["percentual_ausentes"] = (
            relatorio["ausentes"] / total_linhas * 100
        )
    else:
        relatorio["percentual_ausentes"] = 0

    relatorio["momento"] = momento

    return relatorio[
        ["momento", "coluna", "ausentes", "percentual_ausentes"]
    ]


# DIAGNÓSTICO DE ÁRBITRO E QUANTIDADE DE PARTIDAS
def gerar_diagnostico(base):
    """
    Gera os diagnósticos utilizados para documentar as decisões
    da Etapa 3.

    São analisados:
    - disponibilidade de árbitros por liga e temporada;
    - quantidade de partidas por liga e temporada;
    - comparação com o número esperado de partidas.
    """

    # DISPONIBILIDADE DE ÁRBITROS
    diagnostico_arbitro = (
        base
        .groupby(["liga", "temporada"])
        .agg(
            total_jogos=("liga", "size"),
            arbitros_ausentes=("arbitro", lambda coluna: coluna.isna().sum())
        )
        .reset_index()
    )

    diagnostico_arbitro["arbitros_presentes"] = (
        diagnostico_arbitro["total_jogos"]
        - diagnostico_arbitro["arbitros_ausentes"]
    )

    diagnostico_arbitro["percentual_arbitros_presentes"] = (
        diagnostico_arbitro["arbitros_presentes"]
        / diagnostico_arbitro["total_jogos"]
        * 100
    )

    # QUANTIDADE DE PARTIDAS
    quantidade_partidas = (
        base
        .groupby(["liga", "temporada"])
        .size()
        .reset_index(name="partidas")
    )

    def partidas_esperadas(liga, temporada):
        """
        Retorna o número esperado de partidas para cada liga
        e temporada, considerando a composição conhecida das ligas.
        """

        # Bundesliga
        if liga == "D1":
            return 306

        # Ligue 1: 18 equipes a partir de 2023/2024.
        # A temporada 2019/2020 teve encerramento antecipado.
        if liga == "F1":
            if temporada == "2019/2020":
                return 279

            if temporada in ["2023/2024", "2024/2025"]:
                return 306

            return 380

        # Premier League, La Liga e Serie A
        return 380

    quantidade_partidas["esperado"] = quantidade_partidas.apply(
        lambda linha: partidas_esperadas(
            linha["liga"],
            linha["temporada"]
        ),
        axis=1
    )

    quantidade_partidas["diferenca"] = (
        quantidade_partidas["partidas"]
        - quantidade_partidas["esperado"]
    )

    quantidade_partidas["situacao"] = (
        quantidade_partidas["partidas"]
        == quantidade_partidas["esperado"]
    ).map({
        True: "OK",
        False: "FORA DO PADRAO"
    })

    return diagnostico_arbitro, quantidade_partidas


# REMOVER PARTIDAS SEM ESTATÍSTICAS
def remover_partidas_sem_estatisticas(base):
    """
    Remove partidas reais que não possuem nenhuma informação
    nas variáveis estatísticas de interesse.

    Os gols são excluídos deste critério, pois as partidas
    identificadas possuem gols e resultado. A remoção ocorre
    somente quando todas as demais variáveis estatísticas estão
    ausentes simultaneamente.
    """

    colunas_para_verificar = [
        coluna
        for coluna in COLUNAS_ESTATISTICAS
        if coluna not in ["gols_mandante", "gols_visitante"]
    ]

    mascara_sem_estatisticas = base[colunas_para_verificar].isna().all(axis=1)

    partidas_removidas = base[mascara_sem_estatisticas].copy()

    print("\n" + "=" * 60)
    print("REMOÇÃO DE PARTIDAS SEM ESTATÍSTICAS")
    print("=" * 60)

    print(
        f"Partidas identificadas para remoção: "
        f"{len(partidas_removidas)}"
    )

    if len(partidas_removidas) > 0:

        print("\nPartidas removidas:")

        print(
            partidas_removidas[
                [
                    "liga",
                    "temporada",
                    "data",
                    "time_mandante",
                    "time_visitante",
                    "gols_mandante",
                    "gols_visitante"
                ]
            ].to_string(index=False)
        )

    else:
        print("Nenhuma partida sem estatísticas foi encontrada.")

    base_tratada = base[~mascara_sem_estatisticas].copy()

    print(
        f"\nLinhas antes da remoção: {len(base)}"
    )
    print(
        f"Linhas depois da remoção: {len(base_tratada)}"
    )

    return base_tratada, partidas_removidas


# VERIFICAR AUSÊNCIAS NAS COLUNAS ESTATÍSTICAS
def verificar_ausencias_estatisticas(base):
    """
    Identifica registros que ainda possuem valores ausentes
    nas principais colunas estatísticas utilizadas no estudo.

    As linhas encontradas não são removidas nesta etapa.
    """

    colunas_existentes = [
        coluna
        for coluna in COLUNAS_ESTATISTICAS
        if coluna in base.columns
    ]

    linhas_com_ausencias = base[
        base[colunas_existentes].isna().any(axis=1)
    ].copy()

    quantidade_por_coluna = (
        base[colunas_existentes]
        .isna()
        .sum()
    )

    return quantidade_por_coluna, linhas_com_ausencias


# GERAR TEXTO DO RELATÓRIO
def gerar_texto_relatorio(
    base_antes,
    base_depois,
    relatorio_antes,
    relatorio_depois,
    diagnostico_arbitro,
    quantidade_partidas,
    linhas_fantasma_removidas,
    partidas_sem_estatisticas,
    ausencias_estatisticas,
    linhas_com_ausencias
):
    """
    Monta o relatório textual completo da Etapa 3.

    O relatório é autoexplicativo e registra os números,
    diagnósticos e decisões metodológicas desta etapa.
    """

    linhas = []

    linhas.append("=" * 80)
    linhas.append("RELATÓRIO DE DISPONIBILIDADE DOS DADOS - ETAPA 3")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        "Este relatório documenta a análise de disponibilidade dos dados "
        "da base unificada e as decisões de limpeza realizadas na Etapa 3 "
        "do projeto."
    )
    linhas.append("")

    # LIMPEZA
    linhas.append("=" * 80)
    linhas.append("1. LIMPEZA DAS LINHAS FANTASMA")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        f"Linhas originais: {len(base_antes)}"
    )
    linhas.append(
        f"Linhas removidas como fantasmas: {linhas_fantasma_removidas}"
    )
    linhas.append(
        f"Linhas após a remoção dos fantasmas: "
        f"{len(base_antes) - linhas_fantasma_removidas}"
    )
    linhas.append("")
    linhas.append(
        "Foram removidas as linhas identificadas como registros fantasma "
        "nos arquivos CSV originais. O critério operacional utilizado "
        "foi a ausência de gols_mandante, conforme a inspeção realizada "
        "na etapa anterior."
    )
    linhas.append("")

    # PARTIDAS SEM ESTATÍSTICAS
    linhas.append("=" * 80)
    linhas.append("2. REMOÇÃO DE PARTIDAS REAIS SEM ESTATÍSTICAS")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        f"Partidas reais removidas: {len(partidas_sem_estatisticas)}"
    )
    linhas.append("")

    if len(partidas_sem_estatisticas) > 0:
        linhas.append("Partidas removidas:")
        linhas.append(
            partidas_sem_estatisticas[
                [
                    "liga",
                    "temporada",
                    "data",
                    "time_mandante",
                    "time_visitante",
                    "gols_mandante",
                    "gols_visitante"
                ]
            ].to_string(index=False)
        )
        linhas.append("")

    linhas.append(
        "A decisão de remover essas partidas foi tomada porque o impacto "
        "é estatisticamente desprezível: 2 em 18.011 linhas, equivalente "
        "a aproximadamente 0,011% da base após a remoção das linhas fantasma."
    )
    linhas.append("")
    linhas.append(
        "Essas variáveis são centrais para o estudo, especialmente cartões "
        "e faltas. Não foi utilizada imputação por média, mediana ou zero, "
        "pois qualquer uma dessas alternativas introduziria uma suposição "
        "sobre o nível de indisciplina das partidas sem informação observada "
        "que permita sustentá-la metodologicamente."
    )
    linhas.append("")
    linhas.append(
        "Além disso, a manutenção de valores ausentes nessas partidas poderia "
        "propagar o problema para a Etapa 4, especialmente na construção das "
        "janelas deslizantes de 3 a 7 partidas, nas quais valores ausentes no "
        "meio da janela poderiam impedir ou distorcer o cálculo dos atributos "
        "históricos."
    )
    linhas.append("")
    linhas.append(
        "Portanto, as duas partidas reais sem estatísticas foram removidas, "
        "sem imputação dos valores ausentes."
    )
    linhas.append("")

    # DISPONIBILIDADE ANTES
    linhas.append("=" * 80)
    linhas.append("3. DISPONIBILIDADE DOS DADOS - ANTES DA LIMPEZA")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        relatorio_antes[
            ["coluna", "ausentes", "percentual_ausentes"]
        ].to_string(
            index=False,
            formatters={
                "percentual_ausentes": "{:.2f}%".format
            }
        )
    )
    linhas.append("")

    # DISPONIBILIDADE DEPOIS
    linhas.append("=" * 80)
    linhas.append("4. DISPONIBILIDADE DOS DADOS - DEPOIS DA LIMPEZA")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        relatorio_depois[
            ["coluna", "ausentes", "percentual_ausentes"]
        ].to_string(
            index=False,
            formatters={
                "percentual_ausentes": "{:.2f}%".format
            }
        )
    )
    linhas.append("")

    # ÁRBITROS
    linhas.append("=" * 80)
    linhas.append("5. DISPONIBILIDADE DA VARIÁVEL ÁRBITRO")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        "A coluna 'arbitro' foi mantida na base, porém não será utilizada "
        "como atributo do modelo de aprendizado de máquina."
    )
    linhas.append("")
    linhas.append(
        "A análise da fonte mostrou que os dados de árbitro estão disponíveis "
        "apenas para a Premier League (E0). Para D1, F1, I1 e SP1, a coluna "
        "não está presente nos arquivos brutos dessas ligas. Portanto, "
        "essas ausências representam uma limitação de disponibilidade da "
        "fonte, e não valores individuais que possam ser imputados."
    )
    linhas.append("")
    linhas.append(
        diagnostico_arbitro.to_string(
            index=False,
            formatters={
                "percentual_arbitros_presentes": "{:.2f}%".format
            }
        )
    )
    linhas.append("")
    linhas.append(
        "Decisão metodológica: a variável 'arbitro' não será utilizada "
        "como atributo do modelo, pois sua disponibilidade está restrita "
        "a uma única liga. A coluna permanece na base tratada para "
        "preservar a informação original da fonte."
    )
    linhas.append("")

    # PARTIDAS
    linhas.append("=" * 80)
    linhas.append("6. QUANTIDADE DE PARTIDAS POR LIGA E TEMPORADA")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        quantidade_partidas.to_string(index=False)
    )
    linhas.append("")

    linhas.append(
        "A quantidade de partidas é comparada com o número esperado "
        "para cada composição de liga."
    )
    linhas.append("")
    linhas.append(
        "A temporada F1 2019/2020 apresenta 279 partidas. "
        "Esse número não é tratado como erro de leitura, pois a "
        "temporada foi interrompida e encerrada antecipadamente "
        "em razão da pandemia de Covid-19."
    )
    linhas.append("")

    linhas.append(
        "O Conseil d'État francês registra que, em razão da epidemia "
        "de Covid-19, a Ligue de Football Professionnel (LFP) decidiu "
        "em 30 de abril de 2020 encerrar definitivamente a temporada "
        "2019/2020 da Ligue 1 e da Ligue 2. A decisão considerou o "
        "contexto sanitário e a impossibilidade de retomada das "
        "competições nas condições então existentes."
    )
    linhas.append("")

    linhas.append(
        "Fonte principal: Conseil d'État, decisão de 9 de junho de 2020, "
        "\"Ligue 1 de football : le juge des référés du Conseil d'État "
        "valide la fin de la saison et le classement mais suspend les "
        "relégations\"."
    )
    linhas.append(
        "https://conseil-etat.fr/actualites/"
        "ligue-1-de-football-le-juge-des-referes-du-conseil-d-etat-"
        "valide-la-fin-de-la-saison-et-le-classement-mais-suspend-les-relegations"
    )
    linhas.append("")


    # AUSÊNCIAS ESTATÍSTICAS
    linhas.append("=" * 80)
    linhas.append("7. AUSÊNCIAS REMANESCENTES NAS VARIÁVEIS ESTATÍSTICAS")
    linhas.append("=" * 80)
    linhas.append("")

    if len(linhas_com_ausencias) == 0:
        linhas.append(
            "Não foram encontradas ausências nas colunas estatísticas "
            "após a remoção das linhas fantasma."
        )
    else:
        linhas.append(
            "Foram encontradas ausências após a limpeza. Nenhuma dessas "
            "linhas foi removida automaticamente nesta etapa."
        )
        linhas.append("")
        linhas.append("Quantidade de ausentes por coluna:")
        linhas.append(
            ausencias_estatisticas[
                ausencias_estatisticas > 0
            ].to_string()
        )
        linhas.append("")
        linhas.append("Linhas completas que apresentam ausência:")
        linhas.append(
            linhas_com_ausencias.to_string(index=False)
        )

    linhas.append("")

    # BASE FINAL
    linhas.append("=" * 80)
    linhas.append("8. BASE TRATADA")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        f"Linhas originais: {len(base_antes)}"
    )
    linhas.append(
        f"Após remoção das linhas fantasma: "
        f"{len(base_antes) - linhas_fantasma_removidas}"
    )
    linhas.append(
        f"Após remoção das partidas sem estatísticas: "
        f"{len(base_depois)}"
    )
    linhas.append(
        f"Linhas removidas como fantasmas: {linhas_fantasma_removidas}"
    )
    linhas.append(
        f"Partidas reais sem estatísticas removidas: "
        f"{len(partidas_sem_estatisticas)}"
    )
    linhas.append("")
    linhas.append("Colunas da base final:")
    for coluna in base_depois.columns:
        linhas.append(f"- {coluna}")

    linhas.append("")
    linhas.append(
        "A coluna 'arbitro' permanece na base final, embora não seja "
        "utilizada como atributo do modelo."
    )
    linhas.append("")

    linhas.append("=" * 80)
    linhas.append("9. ENCAMINHAMENTO PARA A ETAPA 4")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append(
        "A base tratada salva em dados/processados/base_tratada.csv "
        "constitui a entrada para a próxima etapa do projeto."
    )
    linhas.append(
        "As decisões sobre eventuais ausências estatísticas remanescentes "
        "não foram tomadas automaticamente quando foram identificados "
        "registros incompletos; essas linhas foram apenas documentadas "
        "para avaliação metodológica."
    )
    linhas.append("")

    return "\n".join(linhas)


# ANALISAR DISPONIBILIDADE
def analisar_disponibilidade(base_unificada):
    """
    Executa a Etapa 3 de análise de disponibilidade.

    Remove somente as linhas fantasma identificadas, gera os
    relatórios de disponibilidade antes e depois da limpeza,
    documenta as limitações da variável árbitro, verifica a
    quantidade de partidas por liga e temporada, registra
    eventuais ausências estatísticas remanescentes e salva
    a base tratada e o relatório textual.

    Devolve o DataFrame tratado para permitir o encadeamento
    com as próximas etapas do projeto.
    """

    print("=" * 60)
    print("ETAPA 3 - ANÁLISE DE DISPONIBILIDADE")
    print("=" * 60)

    # Criar pastas de saída
    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    ARQUIVO_RELATORIO.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Relatório antes da limpeza
    relatorio_antes = gerar_relatorio_disponibilidade(
        base_unificada,
        "Antes da limpeza"
    )

    # Remover linhas fantasma
    base_tratada, linhas_fantasma_removidas = remover_linhas_vazias(
        base_unificada
    )

    # Remover partidas reais sem estatísticas
    base_tratada, partidas_sem_estatisticas = (
        remover_partidas_sem_estatisticas(base_tratada)
    )

    # Relatório depois da limpeza completa
    relatorio_depois = gerar_relatorio_disponibilidade(
        base_tratada,
        "Depois da limpeza"
    )

    # Diagnósticos
    diagnostico_arbitro, quantidade_partidas = gerar_diagnostico(
        base_tratada
    )

    # Verificar ausências estatísticas somente depois das duas remoções
    ausencias_estatisticas, linhas_com_ausencias = (
        verificar_ausencias_estatisticas(base_tratada)
    )

    # Gerar relatório completo
    texto_relatorio = gerar_texto_relatorio(
        base_unificada,
        base_tratada,
        relatorio_antes,
        relatorio_depois,
        diagnostico_arbitro,
        quantidade_partidas,
        linhas_fantasma_removidas,
        partidas_sem_estatisticas,
        ausencias_estatisticas,
        linhas_com_ausencias
    )

    # Imprimir relatório no terminal
    print("\n" + texto_relatorio)

    # Salvar relatório em arquivo
    with open(
        ARQUIVO_RELATORIO,
        "w",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(texto_relatorio)

    # Salvar base tratada
    base_tratada.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("ETAPA 3 CONCLUÍDA")
    print("=" * 60)
    print(f"Base tratada salva em: {ARQUIVO_SAIDA}")
    print(f"Relatório salvo em: {ARQUIVO_RELATORIO}")

    return base_tratada


# EXECUTAR A ETAPA SOZINHA
if __name__ == "__main__":

    if not ARQUIVO_ENTRADA.exists():

        print(
            f"[ERRO] Arquivo de entrada não encontrado: "
            f"{ARQUIVO_ENTRADA}"
        )

    else:

        base_unificada = pd.read_csv(
            ARQUIVO_ENTRADA,
            encoding="utf-8-sig"
        )

        analisar_disponibilidade(
            base_unificada
        )