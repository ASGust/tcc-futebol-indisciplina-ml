# DATA UNIFICATION
import pandas as pd
from pathlib import Path


# SETTINGS
RAW_DATA_DIR = Path('data/raw')

PROCESSED_DATA_DIR = Path('data/processed')

OUTPUT_FILE = 'unified_base.csv'


# COLUMN WHITELIST AND RENAMING
# Only these source columns are read; the key order is also the column
# order of the unified table.
COLUMN_RENAMES = {
    'Date': 'date',
    'Referee': 'referee',
    'HomeTeam': 'home_team',
    'AwayTeam': 'away_team',

    'FTHG': 'home_goals',
    'FTAG': 'away_goals',
    'FTR': 'result',

    'HS': 'home_shots',
    'AS': 'away_shots',

    'HST': 'home_shots_on_target',
    'AST': 'away_shots_on_target',

    'HC': 'home_corners',
    'AC': 'away_corners',

    'HF': 'home_fouls',
    'AF': 'away_fouls',

    'HY': 'home_yellow_cards',
    'AY': 'away_yellow_cards',

    'HR': 'home_red_cards',
    'AR': 'away_red_cards'
}

ALLOWED_COLUMNS = list(COLUMN_RENAMES)

# Match totals: total column -> (home column, away column)
MATCH_TOTALS = {
    'total_yellow_cards': ('home_yellow_cards', 'away_yellow_cards'),
    'total_red_cards': ('home_red_cards', 'away_red_cards'),
    'total_fouls': ('home_fouls', 'away_fouls'),
    'total_goals': ('home_goals', 'away_goals')
}


def convert_season(season_code):
    """Converts a season code to YYYY/YYYY (e.g. 1516 -> 2015/2016)."""

    start_year = 2000 + int(season_code[:2])
    end_year = 2000 + int(season_code[2:])

    return f'{start_year}/{end_year}'


def collect_headers(files):
    """
    Returns the union of the column names of all raw files, reading only
    their headers, to inspect the source before processing any data.
    """

    all_columns = set()

    for file in files:

        try:

            header = pd.read_csv(file, encoding='latin-1', nrows=0)

            all_columns.update(column.strip() for column in header.columns)

        except Exception as error:

            print(f'[ERROR] Could not read the header of {file.name}: {error}')

    return sorted(all_columns)


def check_possession_and_passes(columns):
    """Looks for header names related to ball possession and passes."""

    possession_columns = [
        column
        for column in columns
        if 'poss' in column.lower()
    ]

    pass_columns = [
        column
        for column in columns
        if 'pass' in column.lower()
    ]

    print('\n' + '=' * 60)
    print('BALL POSSESSION AND PASSES CHECK')
    print('=' * 60)

    if possession_columns:
        print('Possible possession columns:')
        for column in possession_columns:
            print(f'  - {column}')
    else:
        print('No ball possession column found.')

    if pass_columns:
        print('\nPossible pass columns:')
        for column in pass_columns:
            print(f'  - {column}')
    else:
        print('No pass column found.')


def read_file(file):
    """
    Reads a CSV keeping only the allowed columns; any allowed column
    missing from the file is created with NaN.
    """

    header = pd.read_csv(file, encoding='latin-1', nrows=0)

    # Stripped so an extra space in one file does not break the comparison
    existing_columns = [column.strip() for column in header.columns]

    columns_to_read = [
        column
        for column in ALLOWED_COLUMNS
        if column in existing_columns
    ]

    table = pd.read_csv(file, encoding='latin-1', usecols=columns_to_read)

    table.columns = [column.strip() for column in table.columns]

    for column in ALLOWED_COLUMNS:

        if column not in table.columns:
            table[column] = pd.NA

    return table[ALLOWED_COLUMNS]


def add_league_and_season(table, file):
    """Gets league and season from the file name (E0_2324 -> E0, 2023/2024)."""

    league, season_code = file.stem.split('_')

    table['league'] = league
    table['season'] = convert_season(season_code)

    return table


def create_match_totals(table):
    """
    Creates the match totals of yellow cards, red cards, fouls and goals.
    If either side's value is missing, the total is missing too.
    """

    for total_column, (home_column, away_column) in MATCH_TOTALS.items():

        table[total_column] = table[[home_column, away_column]].sum(
            axis=1,
            min_count=2
        )

    return table


def standardize_date(table):

    table['date'] = pd.to_datetime(
        table['date'],
        format='mixed',
        dayfirst=True,
        errors='coerce'
    )

    return table


# MAIN PROGRAM
def unify_files():
    """
    Runs Step 2: builds the unified table from the raw CSVs, saves it and
    returns it.
    """

    print('=' * 60)
    print('STEP 2 - BUILDING THE UNIFIED TABLE')
    print('=' * 60)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DATA_DIR.glob('*.csv'))

    if not files:

        print('\n[ERROR] No CSV file was found in:')
        print(RAW_DATA_DIR)

        return

    print(f'\nFiles found: {len(files)}')

    all_columns = collect_headers(files)

    print('\n' + '=' * 60)
    print('ALL COLUMNS FOUND')
    print('=' * 60)

    for column in all_columns:
        print(column)

    check_possession_and_passes(all_columns)

    # Read and prepare each file
    tables = []

    for file in files:

        print(f'\nProcessing: {file.name}')

        try:

            table = read_file(file)
            table = add_league_and_season(table, file)
            table = table.rename(columns=COLUMN_RENAMES)
            table = create_match_totals(table)

            tables.append(table)

            print(f'  Matches loaded: {len(table)}')

        except Exception as error:

            print(f'  [ERROR] Could not process {file.name}: {error}')

    if not tables:

        print('\n[ERROR] No file could be processed.')

        return

    unified_base = pd.concat(tables, ignore_index=True)

    unified_base = standardize_date(unified_base)

    unified_base = unified_base.sort_values(by='date').reset_index(drop=True)

    # League, season and date first, then the remaining columns
    leading_columns = ['league', 'season', 'date']

    other_columns = [
        column
        for column in unified_base.columns
        if column not in leading_columns
    ]

    unified_base = unified_base[leading_columns + other_columns]

    output_path = PROCESSED_DATA_DIR / OUTPUT_FILE

    unified_base.to_csv(output_path, index=False, encoding='utf-8-sig')

    # FINAL RESULT
    print('\n' + '=' * 60)
    print('FINAL RESULT')
    print('=' * 60)

    print(f'\nNumber of rows: {unified_base.shape[0]}')
    print(f'Number of columns: {unified_base.shape[1]}')

    print('\nFirst 5 rows:')
    print(unified_base.head(5).to_string(index=False))

    print('\nMissing values per column:')
    print(unified_base.isna().sum())

    print('\nBase saved to:')
    print(output_path)

    return unified_base


# RUN THE PROGRAM
if __name__ == '__main__':
    unify_files()
