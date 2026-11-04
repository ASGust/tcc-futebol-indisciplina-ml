# FINAL COLUMN SELECTION
#
# Step 6 of the pipeline: keeps the 108 modeling columns (identification,
# pre-match date attributes and the 100 rolling windows).
#
# No row is removed; the window NaN values are left for the experiments
# step.
#
# Input:
# data/processed/attributes_base.csv
#
# Output:
# data/processed/final_base.csv
import pandas as pd
from pathlib import Path


# SETTINGS
INPUT_FILE = Path('data/processed/attributes_base.csv')
OUTPUT_FILE = Path('data/processed/final_base.csv')

# Includes the target (result) and weekday/month, known before the match
IDENTIFICATION_COLUMNS = [
    'league',
    'season',
    'date',
    'home_team',
    'away_team',
    'result',
    'weekday',
    'month'
]

# Window column pattern: <side>_<statistic>_avg_last<N>
SIDES = ['home', 'away']

WINDOW_STATISTICS = [
    'points',
    'indiscipline',
    'yellow_cards',
    'red_cards',
    'fouls',
    'goals_scored',
    'goals_conceded',
    'shots',
    'shots_on_target',
    'corners'
]

WINDOW_SIZES = [3, 4, 5, 6, 7]


def list_window_columns():
    """
    Lists the 100 window columns in the attributes base order: side, then
    window size, then statistic.
    """

    return [
        f'{side}_{statistic}_avg_last{window_size}'
        for side in SIDES
        for window_size in WINDOW_SIZES
        for statistic in WINDOW_STATISTICS
    ]


def check_columns_present(base, columns):
    """
    Raises an error if any expected column is missing, so an incomplete
    final base is never saved silently.
    """

    missing_columns = [
        column
        for column in columns
        if column not in base.columns
    ]

    if missing_columns:
        raise KeyError(
            f'Expected columns missing from the attributes base: '
            f'{missing_columns}'
        )


def report_window_nan(base, window_columns):
    """
    Prints the NaN count per window column and the rows with NaN per window
    size, and returns the per-column counts.
    """

    nan_per_column = base[window_columns].isna().sum()

    print('\n' + '-' * 70)
    print('MISSING VALUES (NaN) PER WINDOW COLUMN')
    print('-' * 70)

    for column, count in nan_per_column.items():
        print(f'{column:<40} {count:>5}')

    print('\n' + '-' * 70)
    print('ROWS WITH NaN PER WINDOW SIZE')
    print('-' * 70)

    for window_size in WINDOW_SIZES:

        size_columns = [
            column
            for column in window_columns
            if column.endswith(f'_avg_last{window_size}')
        ]

        rows_with_nan = int(base[size_columns].isna().any(axis=1).sum())

        print(f'Window last{window_size}: {rows_with_nan} row(s) with NaN')

    return nan_per_column


# MAIN FUNCTION
def select_final_columns(attributes_base):
    """Runs Step 6: selects the final columns, saves them and returns them."""

    print('=' * 70)
    print('STEP 6 - FINAL COLUMN SELECTION')
    print('=' * 70)

    window_columns = list_window_columns()
    final_columns = IDENTIFICATION_COLUMNS + window_columns

    check_columns_present(attributes_base, final_columns)

    final_base = attributes_base[final_columns].copy()

    print(f'\nColumns kept ({len(final_columns)}):')

    for position, column in enumerate(final_columns, start=1):
        print(f'{position:>3}. {column}')

    report_window_nan(final_base, window_columns)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    final_base.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    print('\n' + '=' * 70)
    print('STEP 6 COMPLETED')
    print('=' * 70)

    print(
        f'Final base shape: '
        f'{len(final_base)} rows x '
        f'{len(final_base.columns)} columns'
    )

    print(f'Final base saved to: {OUTPUT_FILE}')

    return final_base


# RUN THE STEP ON ITS OWN
if __name__ == '__main__':

    if not INPUT_FILE.exists():

        print(f'[ERROR] Input file not found: {INPUT_FILE}')

    else:

        attributes_base = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')

        select_final_columns(attributes_base)
