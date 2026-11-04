# DERIVED ATTRIBUTES
#
# Computes attributes from each match on its own, without using any
# other match.
#
# Input:
# data/processed/clean_base.csv
import numpy as np
import pandas as pd
from pathlib import Path


# SETTINGS
INPUT_FILE = Path('data/processed/clean_base.csv')

# Points per result: H = home win, D = draw, A = away win
HOME_POINTS = {'H': 3, 'D': 1, 'A': 0}
AWAY_POINTS = {'H': 0, 'D': 1, 'A': 3}

CREATED_COLUMNS = [
    'home_points',
    'away_points',
    'home_indiscipline_index',
    'away_indiscipline_index',
    'total_indiscipline_index',
    'home_discipline_per_foul',
    'away_discipline_per_foul',
    'home_shot_efficiency',
    'away_shot_efficiency',
    'weekday',
    'month'
]


# HELPER FUNCTIONS
def safe_ratio(numerator, denominator):
    """
    Divides two columns, returning zero when the denominator is zero, so
    no NaN (0/0) or infinite (x/0) values are added.
    """

    return (
        numerator
        .div(denominator)
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )


def calculate_points(base):
    """
    Computes each team's points from the result; matches without a known
    result get zero points.
    """

    base['home_points'] = base['result'].map(HOME_POINTS).fillna(0).astype(int)
    base['away_points'] = base['result'].map(AWAY_POINTS).fillna(0).astype(int)

    return base


def calculate_indiscipline_indexes(base):
    """
    Computes each team's indiscipline index (yellow = 1, red = 2) and the
    match total.
    """

    base['home_indiscipline_index'] = (
        base['home_yellow_cards'] + 2 * base['home_red_cards']
    )

    base['away_indiscipline_index'] = (
        base['away_yellow_cards'] + 2 * base['away_red_cards']
    )

    base['total_indiscipline_index'] = (
        base['home_indiscipline_index'] + base['away_indiscipline_index']
    )

    return base


def calculate_discipline_per_foul(base):
    """Computes each team's cards per foul: (yellow + red cards) / fouls."""

    base['home_discipline_per_foul'] = safe_ratio(
        base['home_yellow_cards'] + base['home_red_cards'],
        base['home_fouls']
    )

    base['away_discipline_per_foul'] = safe_ratio(
        base['away_yellow_cards'] + base['away_red_cards'],
        base['away_fouls']
    )

    return base


def calculate_shot_efficiency(base):
    """Computes each team's shot efficiency: shots on target / shots."""

    base['home_shot_efficiency'] = safe_ratio(
        base['home_shots_on_target'],
        base['home_shots']
    )

    base['away_shot_efficiency'] = safe_ratio(
        base['away_shots_on_target'],
        base['away_shots']
    )

    return base


def calculate_time_attributes(base):
    """Extracts the weekday name and the month number from the match date."""

    base['weekday'] = base['date'].dt.day_name()
    base['month'] = base['date'].dt.month

    return base


# MAIN FUNCTION
def calculate_derived_attributes(clean_base):
    """
    Runs Step 4: adds the CREATED_COLUMNS attributes, computed only from
    each match's own data, and returns the base.
    """

    print('\n' + '=' * 70)
    print('STEP 4 - DERIVED ATTRIBUTES')
    print('=' * 70)

    base = clean_base.copy()

    rows_before = len(base)

    print('\nShape before feature engineering:')
    print(f'Rows     : {rows_before}')
    print(f'Columns  : {len(base.columns)}')

    base = calculate_points(base)
    base = calculate_indiscipline_indexes(base)
    base = calculate_discipline_per_foul(base)
    base = calculate_shot_efficiency(base)
    base = calculate_time_attributes(base)

    print('\nShape after feature engineering:')
    print(f'Rows     : {len(base)}')
    print(f'Columns  : {len(base.columns)}')

    if len(base) == rows_before:
        print('[OK] The number of rows was preserved.')
    else:
        print('[WARNING] The number of rows changed.')

    print('\nCreated columns:')
    for column in CREATED_COLUMNS:
        print(f' - {column}')

    # Missing values in the created columns
    print('\n' + '-' * 70)
    print('MISSING VALUES CHECK IN THE CREATED COLUMNS')
    print('-' * 70)

    missing_values = base[CREATED_COLUMNS].isna().sum()

    for column, count in missing_values[missing_values > 0].items():
        print(f'[WARNING] {column}: {count} missing value(s).')

    if missing_values.sum() == 0:
        print('[OK] No missing value was introduced in the created columns.')

    # Infinite values in the created columns
    print('\n' + '-' * 70)
    print('INFINITE VALUES CHECK IN THE CREATED COLUMNS')
    print('-' * 70)

    infinite_values = base[CREATED_COLUMNS].isin([np.inf, -np.inf]).sum()

    if infinite_values.sum() > 0:
        print('[WARNING] Infinite values were found:')
        print(infinite_values[infinite_values > 0])
    else:
        print('[OK] No infinite value was found in the created columns.')

    print("\n'referee' column check:")
    print(f"Missing values in referee: {base['referee'].isna().sum()}")
    print(
        "Note: the gaps in 'referee' were already present in the clean "
        'base and are not considered missing values introduced by Step 4.'
    )

    print('\n' + '-' * 70)
    print('FIRST 5 ROWS AFTER FEATURE ENGINEERING')
    print('-' * 70)

    print(base.head(5).to_string(index=False))

    return base


# RUN THE STEP ON ITS OWN
if __name__ == '__main__':

    if not INPUT_FILE.exists():

        print(f'[ERROR] Input file not found: {INPUT_FILE}')

    else:

        clean_base = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')

        # The CSV stores dates as text
        clean_base['date'] = pd.to_datetime(clean_base['date'], errors='coerce')

        calculate_derived_attributes(clean_base)
