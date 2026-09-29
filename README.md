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
próprio dentro de `src/`.

### Etapas do pipeline
| Etapa | Script | Status |
|---|---|---|
| 1. Download com cache | `src/etapa1_download.py` | Concluída |
| 2. Unificação da base | `src/etapa2_unificacao.py` | Concluída |
| 3. Análise de disponibilidade e limpeza | `src/etapa3_disponibilidade.py` | Concluída |
| 4. Engenharia de atributos | `src/etapa4_atributos.py` | Em andamento |
| 5. Construção e treinamento dos modelos | — | Pendente |
| 6. Avaliação e análise dos resultados | — | Pendente |

### Resumo das decisões já tomadas (Etapas 1 a 3)
- Foi confirmado empiricamente que a fonte **não disponibiliza** dados
  de posse de bola ou passes completos para nenhuma das ligas.
- A coluna de **árbitro** está disponível apenas para a Premier League
  (E0); nas demais ligas (D1, F1, I1, SP1), essa informação não existe
  nos arquivos originais. Por isso, `arbitro` é mantida na base para
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
`resultados/tabelas/relatorio_disponibilidade.txt`.

## Estrutura do repositório
```
tcc-futebol-indisciplina-ml/
├── main.py                          # executa o pipeline em sequência
├── src/
│   ├── etapa1_download.py
│   ├── etapa2_unificacao.py
│   ├── etapa3_disponibilidade.py
│   └── etapa4_atributos.py          # em construção
├── dados/                           # criada automaticamente pelo código
│   ├── brutos/                      # CSVs originais baixados da fonte
│   └── processados/                 # bases unificada e tratada
├── resultados/
│   └── tabelas/                     # relatórios e tabelas geradas
├── notebooks/                       # análises exploratórias (opcional)
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
   python src/etapa3_disponibilidade.py
   ```
   (nesse caso, a etapa lê a base já processada em
   `dados/processados/`, sem precisar rodar as etapas anteriores).

## Tecnologias
- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Jupyter Notebook

## Variáveis analisadas
- Faltas, cartões amarelos e cartões vermelhos (mandante, visitante e totais)
- Chutes e chutes a gol (mandante e visitante)
- Escanteios (mandante e visitante)
- Gols e resultado da partida
- Liga, temporada, data, times mandante e visitante
- Árbitro (disponível apenas para a Premier League; não utilizado como
  atributo do modelo — ver seção Metodologia)

## Modelos
Serão avaliados modelos de aprendizado de máquina supervisionado para
classificação dos resultados das partidas, utilizando como entrada os
atributos derivados na Etapa 4 (incluindo indicadores históricos de
indisciplina calculados em janelas deslizantes de partidas anteriores).