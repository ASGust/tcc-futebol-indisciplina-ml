#PIPELINE COMPLETO DO PROJETO
# Encadeia as Etapas 1 a 4, repassando o DataFrame de uma etapa
# para a próxima. Cada etapa só roda se a anterior for bem-sucedida.
#
# Execução (a partir da raiz do projeto):
#   python main.py
import sys
from pathlib import Path

from prepare.etapa1_download import baixar_todos_os_arquivos
from prepare.etapa2_unificacao import unificar_arquivos
from prepare.etapa3_disponibilidade import analisar_disponibilidade
from prepare.etapa4_atributos import (
    calcular_atributos_derivados,
    calcular_janelas_deslizantes,
    ARQUIVO_SAIDA as ARQUIVO_BASE_ATRIBUTOS
)


#CONFIGURAÇÕES
# Arquivo de categorização gerado pela Parte 2 da Etapa 4
ARQUIVO_CATEGORIZACAO = Path(
    "resultados/tabelas/categorizacao_colunas.json"
)


def interromper(mensagem):
    """
    Avisa em qual ponto o pipeline parou e encerra o programa
    com código de erro, para que nenhuma etapa seguinte rode.
    """

    print(f"\n[main] [ERRO] {mensagem}")
    print("[main] Pipeline interrompido.")

    sys.exit(1)


#PROGRAMA PRINCIPAL
def main():

    # ETAPA 1 — DOWNLOAD
    print("\n[main] Etapa 1/4: download...")

    resumo_download = baixar_todos_os_arquivos()

    # Sem arquivos baixados nem em cache, não há o que unificar.
    arquivos_disponiveis = (
        resumo_download["baixados"] + resumo_download["cache"]
    )

    if arquivos_disponiveis == 0:
        interromper(
            "Nenhum arquivo CSV disponível (0 baixados e 0 em cache)."
        )


    # ETAPA 2 — UNIFICAÇÃO
    print("\n[main] Etapa 2/4: unificação...")

    base_unificada = unificar_arquivos()

    if base_unificada is None:
        interromper(
            "A unificação não gerou base (nenhum CSV encontrado "
            "ou nenhum pôde ser processado)."
        )


    # ETAPA 3 — DISPONIBILIDADE E LIMPEZA
    print("\n[main] Etapa 3/4: disponibilidade e limpeza...")

    try:
        base_tratada = analisar_disponibilidade(base_unificada)

    except Exception as erro:
        interromper(f"Falha na Etapa 3: {erro}")


    # ETAPA 4 — ENGENHARIA DE ATRIBUTOS
    print("\n[main] Etapa 4/4: engenharia de atributos...")

    try:
        # Parte 1 — atributos derivados por partida
        base_com_atributos = calcular_atributos_derivados(base_tratada)

        # Parte 2 — janelas deslizantes (também salva a categorização)
        base_final = calcular_janelas_deslizantes(base_com_atributos)

        # A função da Parte 2 não salva a base final; o salvamento
        # é feito aqui, no mesmo arquivo e codificação da Etapa 4.
        ARQUIVO_BASE_ATRIBUTOS.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        base_final.to_csv(
            ARQUIVO_BASE_ATRIBUTOS,
            index=False,
            encoding="utf-8-sig"
        )

    except Exception as erro:
        interromper(f"Falha na Etapa 4: {erro}")


    # RESUMO FINAL
    print("\n" + "=" * 70)
    print("[main] PIPELINE CONCLUÍDO")
    print("=" * 70)

    print(
        f"Dimensões finais da base: "
        f"{len(base_final)} linhas x "
        f"{len(base_final.columns)} colunas"
    )

    print("\nArquivos principais gerados:")
    print(f" - {ARQUIVO_BASE_ATRIBUTOS.as_posix()}")
    print(f" - {ARQUIVO_CATEGORIZACAO.as_posix()}")
    print("=" * 70)


# EXECUTAR O PIPELINE
if __name__ == "__main__":
    main()
