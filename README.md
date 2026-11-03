# Avaliando o impacto da indisciplina em jogos futuros utilizando aprendizado de máquina
Projeto de Trabalho de Conclusão de Curso (Engenharia de Computação)
desenvolvido com o objetivo de analisar a relação entre o histórico de
indisciplina das equipes (faltas, cartões amarelos e vermelhos) e os
resultados de partidas futuras de futebol profissional.

## Objetivo
Analisar como indicadores históricos de indisciplina: faltas, cartões
amarelos e cartões vermelhos, podem ser utilizados para prever ou
explicar o desempenho das equipes em partidas futuras, por meio de
técnicas de aprendizado de máquina.

## Fonte de dados
Os dados utilizados são públicos e provenientes do
[football-data.co.uk](https://www.football-data.co.uk/data.php), que
disponibiliza estatísticas de partidas por liga e temporada em formato CSV.

- **Ligas:** Premier League (E0), La Liga (SP1), Serie A (I1),
  Bundesliga (D1) e Ligue 1 (F1).
- **Temporadas:** 2015/2016 até 2024/2025 (10 temporadas por liga).
- **Colunas de apostas/odds foram deliberadamente excluídas** do
  conjunto de dados utilizado, por não fazerem parte do escopo deste
  estudo.

## Metodologia
O projeto utiliza técnicas de análise de dados e aprendizado de máquina
supervisionado para identificar padrões entre indicadores disciplinares
e resultados de partidas. O pipeline de dados foi construído em etapas
sequenciais e independentes, cada uma implementada como um script
próprio dentro de `prepare/`.

O código segue uma estrutura funcional: cada etapa é composta por
funções que recebem e devolvem DataFrames, sem uso de classes (POO).
A estruturação funcional foi adotada por refletir melhor o fluxo de um
pipeline de dados em etapas sequenciais, sem necessidade de estado
compartilhado entre entidades, evitando a complexidade adicional de
classes sem benefício real.

### Etapas do pipeline
| Etapa | Script | Status |
|---|---|---|
| 1. Download com cache | `prepare/step1_download.py` | Concluída |
| 2. Unificação da base | `prepare/step2_unification.py` | Concluída |
| 3. Análise de disponibilidade e limpeza | `prepare/step3_availability.py` | Concluída |
| 4. Atributos derivados por partida | `prepare/step4_derived_attributes.py` | Concluída |
| 5. Janelas deslizantes (médias das 3 a 7 partidas anteriores) | `prepare/step5_rolling_windows.py` | Concluída |
| 6. Seleção final de colunas | `prepare/step6_final_selection.py` | Concluída |
| 7. Construção e treinamento dos modelos (modelagem, etapa futura separada da preparação de dados) | — | Pendente |
| 8. Avaliação e análise dos resultados | — | Pendente |

### Resumo das decisões já tomadas (Etapas 1 a 3)
- Foi confirmado empiricamente que a fonte **não disponibiliza** dados
  de posse de bola ou passes completos para nenhuma das ligas.
- A coluna de **árbitro** está disponível apenas para a Premier League
  (E0); nas demais ligas (D1, F1, I1, SP1), essa informação não existe
  nos arquivos originais. Por isso, `referee` é mantida na base para
  preservar a informação da fonte, mas **não é utilizada como atributo
  do modelo**.
- Foram removidos registros identificados como artefatos de leitura
  (linhas totalmente vazias no fim de alguns arquivos) e partidas reais
  sem nenhuma estatística de jogo disponível (2 casos, impacto
  estatisticamente desprezível).
- A temporada 2019/2020 da Ligue 1 (F1) possui 279 partidas em vez de
  380, por ter sido encerrada antecipadamente pela federação francesa
  devido à pandemia de Covid-19 — tratado como limitação documentada,
  não como erro de leitura.

O relatório completo dessa análise está em
`results/tables/availability_report.txt`.

## Estrutura do repositório
```
tcc-futebol-indisciplina-ml/
├── main.py                          # executa o pipeline em sequência
├── prepare/
│   ├── step1_download.py
│   ├── step2_unification.py
│   ├── step3_availability.py
│   ├── step4_derived_attributes.py
│   ├── step5_rolling_windows.py
│   └── step6_final_selection.py
├── data/                            # criada automaticamente pelo código
│   ├── raw/                         # CSVs originais baixados da fonte
│   └── processed/
│       ├── unified_base.csv         # Etapa 2
│       ├── clean_base.csv           # Etapa 3
│       ├── attributes_base.csv      # Etapas 4 e 5
│       └── final_base.csv           # Etapa 6 (base final para modelagem)
├── results/
│   └── tables/
│       ├── availability_report.txt       # Etapa 3
│       └── column_categorization.json    # Etapa 5
├── requirements.txt
├── .gitignore
└── README.md
```

## Como executar
1. Clone o repositório e entre na pasta do projeto.
2. Crie um ambiente virtual (recomendado) e instale as dependências:
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
3. Execute o pipeline completo a partir da raiz do projeto:
   ```
   python main.py
   ```
   Ou execute uma etapa individualmente, por exemplo:
   ```
   python prepare/step3_availability.py
   ```
   (nesse caso, a etapa lê a base já processada em
   `data/processed/`, sem precisar rodar as etapas anteriores).

## Tecnologias
- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Jupyter Notebook

## Variáveis da base final
A base final (`data/processed/final_base.csv`) tem 18009 partidas e
108 colunas:

- **Identificação e controle (8):** `league`, `season`, `date`,
  `home_team`, `away_team`, `result` (alvo: `H`, `D` ou `A`), `weekday`
  e `month`. `weekday` e `month` vêm apenas da data da partida, conhecida
  antes do jogo, e por isso podem ser usadas como atributos do modelo.
- **Janelas deslizantes (100):** colunas no padrão
  `<side>_<statistic>_avg_last<N>`, com a média das N partidas anteriores
  de cada time (por exemplo, `home_points_avg_last3`):
  - `<side>`: `home` (mandante) ou `away` (visitante);
  - `<statistic>`: `points`, `indiscipline`, `yellow_cards`, `red_cards`,
    `fouls`, `goals_scored`, `goals_conceded`, `shots`,
    `shots_on_target` e `corners`;
  - `<N>`: de 3 a 7.

As primeiras partidas de cada time não têm histórico suficiente e ficam
com valores ausentes nas janelas correspondentes; o tratamento desses
casos fica para a etapa de experimentos.

As estatísticas da própria partida (gols, chutes, cartões etc.) e a
coluna `referee` existem nas bases intermediárias, mas não entram na
base final: as primeiras só são conhecidas depois do jogo (vazamento de
dados), e `referee` está disponível apenas para a Premier League.

## Modelos
Serão avaliados modelos de aprendizado de máquina supervisionado para
classificação dos resultados das partidas, utilizando como entrada a
base final da Etapa 6 (incluindo indicadores históricos de indisciplina
calculados em janelas deslizantes de partidas anteriores).