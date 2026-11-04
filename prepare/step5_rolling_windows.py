# ROLLING WINDOWS OF HISTORICAL PERFORMANCE
#
# Computes each team's averages over its 3 to 7 previous matches.
#
# DATA LEAKAGE WARNING:
# Only earlier matches are used: shift(1) keeps the current match out of
# its own history. Only these averages are candidate model inputs; the
# Step 4 attributes stay available for exploratory analysis.
#
# Input:
# data/processed/clean_base.csv (through the Step 4 attributes)
#
# Output:
# data/processed/attributes_base.csv
# results/tables/column_categorization.json
import json
import pandas as pd
from pathlib import Path


# SETTINGS
INPUT_FILE = Path('data/processed/clean_base.csv')
OUTPUT_FILE = Path('data/processed/attributes_base.csv')
CATEGORIZATION_FILE = Path('results/tables/column_categorization.json')

WINDOW_SIZES = [3, 4, 5, 6, 7]

DISCIPLINARY_STATISTICS = [
    'indiscipline',
    'yellow_cards',
    'red_cards',
    'fouls'
]

PERFORMANCE_STATISTICS = [
    'points',
    'goals_scored',
    'goals_conceded',
    'shots',
    'shots_on_target',
    'corners'
]

# Order used for the window columns
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

# Source column of each history statistic, per side of the match
HISTORY_SOURCE_COLUMNS = {
    'home': {
        'team': 'home_team',
        'points': 'home_points',
        'indiscipline': 'home_indiscipline_index',
        'yellow_cards': 'home_yellow_cards',
        'red_cards': 'home_red_cards',
        'fouls': 'home_fouls',
        'goals_scored': 'home_goals',
        'goals_conceded': 'away_goals',
        'shots': 'home_shots',
        'shots_on_target': 'home_shots_on_target',
        'corners': 'home_corners'
    },
    'away': {
        'team': 'away_team',
        'points': 'away_points',
        'indiscipline': 'away_indiscipline_index',
        'yellow_cards': 'away_yellow_cards',
        'red_cards': 'away_red_cards',
        'fouls': 'away_fouls',
        'goals_scored': 'away_goals',
        'goals_conceded': 'home_goals',
        'shots': 'away_shots',
        'shots_on_target': 'away_shots_on_target',
        'corners': 'away_corners'
    }
}


def window_column(statistic, window_size):
    return f'{statistic}_avg_last{window_size}'


def window_columns(window_sizes=WINDOW_SIZES):
    """
    Lists the window columns by window size, then statistic
    (points_avg_last3, ..., corners_avg_last7).
    """

    return [
        window_column(statistic, window_size)
        for window_size in window_sizes
        for statistic in WINDOW_STATISTICS
    ]


def build_team_history(base):
    """
    Reshapes the base into long format (one row per team and match, home
    or away), sorted by team and date.
    """

    side_histories = []

    for side, source_columns in HISTORY_SOURCE_COLUMNS.items():

        side_history = pd.DataFrame({
            'match_id': base.index,
            'date': base['date'],
            'league': base['league'],
            'season': base['season'],
            'side': side
        })

        for history_column, source_column in source_columns.items():
            side_history[history_column] = base[source_column].values

        side_histories.append(side_history)

    team_history = pd.concat(side_histories, ignore_index=True)

    team_history['date'] = pd.to_datetime(team_history['date'], errors='coerce')

    team_history = team_history.sort_values(
        ['team', 'date', 'match_id']
    ).reset_index(drop=True)

    return team_history[
        ['match_id', 'date', 'league', 'season', 'team', 'side']
        + WINDOW_STATISTICS
    ]


def calculate_rolling_averages(team_history, window_sizes=WINDOW_SIZES):
    """
    Adds each team's averages of its previous N matches (shift(1) excludes
    the current one); NaN while the team has fewer than N matches.
    """

    history_with_averages = team_history.sort_values(
        ['team', 'date', 'match_id']
    ).reset_index(drop=True)

    team_groups = history_with_averages.groupby('team')[WINDOW_STATISTICS]

    for window_size in window_sizes:

        averages = team_groups.transform(
            lambda series: series.shift(1).rolling(
                window=window_size,
                min_periods=window_size
            ).mean()
        )

        averages.columns = [
            window_column(statistic, window_size)
            for statistic in averages.columns
        ]

        history_with_averages[averages.columns] = averages

    return history_with_averages


def merge_history_into_base(base, history_with_averages):
    """
    Adds the averages back to the match base, prefixed home_/away_ and
    joined by match id and side.
    """

    result_base = base.copy()
    result_base['_match_id'] = result_base.index

    average_columns = window_columns()

    for side in HISTORY_SOURCE_COLUMNS:

        side_averages = history_with_averages.loc[
            history_with_averages['side'] == side,
            ['match_id'] + average_columns
        ].rename(
            columns={column: f'{side}_{column}' for column in average_columns}
        )

        result_base = result_base.merge(
            side_averages,
            left_on='_match_id',
            right_on='match_id',
            how='left'
        ).drop(columns='match_id')

    return result_base.drop(columns='_match_id')


def check_data_leakage(base, team_history, sample_size=3):
    """
    For a few sample matches, shows the home team's last 3 earlier matches
    and checks they all come before the current one.
    """

    print('\n' + '-' * 70)
    print('DATA LEAKAGE CHECK')
    print('-' * 70)

    # Fixed seed so the results can be reproduced
    test_matches = base.sample(n=min(sample_size, len(base)), random_state=42)

    for number, (_, match) in enumerate(test_matches.iterrows(), start=1):

        current_date = match['date']
        home_team = match['home_team']

        previous_matches = team_history[
            (team_history['team'] == home_team)
            & (team_history['date'] < current_date)
        ].sort_values(['date', 'match_id'], ascending=False).head(3)

        print(f'\nTest match {number}:')
        print(f"Current date  : {current_date.strftime('%Y-%m-%d')}")
        print(f'Home team     : {home_team}')
        print(f"Away team     : {match['away_team']}")

        print("\nHome team's last 3 earlier matches used as history:")

        if len(previous_matches) == 0:
            print('No earlier match available.')
            continue

        for _, history_row in previous_matches.iterrows():
            print(
                f" - {history_row['date'].strftime('%Y-%m-%d')} "
                f"| {history_row['team']} "
                f"| {history_row['side']}"
            )

        if (previous_matches['date'] < current_date).all():
            print('[OK] All dates used are strictly before the current match.')
        else:
            print('[WARNING] A date that is not before the current match was found.')


def build_missing_report(base, window_sizes=WINDOW_SIZES):
    """
    Counts, per window size, the rows with NaN and the teams affected.
    Rows are neither removed nor filled.
    """

    report = {}

    print('\n' + '-' * 70)
    print('MISSING VALUES REPORT IN THE HISTORICAL WINDOWS')
    print('-' * 70)

    for window_size in window_sizes:

        size_columns = [
            f'{side}_{window_column(statistic, window_size)}'
            for side in HISTORY_SOURCE_COLUMNS
            for statistic in WINDOW_STATISTICS
        ]

        rows_with_nan = base[size_columns].isna().any(axis=1)

        # Both home and away teams of the affected rows
        affected_teams = (
            set(base.loc[rows_with_nan, 'home_team'])
            | set(base.loc[rows_with_nan, 'away_team'])
        )

        report[window_size] = {
            'rows_with_nan': int(rows_with_nan.sum()),
            'distinct_teams_affected': len(affected_teams)
        }

        print(
            f'Window last{window_size}: '
            f'{report[window_size]["rows_with_nan"]} row(s) with NaN | '
            f'{len(affected_teams)} distinct team(s) affected'
        )

    return report


def build_column_categorization(base):
    """
    Splits the base columns into five groups:
    1. identification
    2. pre-match date attributes (weekday, month; usable in the model)
    3. current match attributes (do not use as model input: data leakage)
    4. disciplinary windows
    5. performance windows
    Used to build feature sets with and without indiscipline attributes.
    """

    identification = [
        'league',
        'season',
        'date',
        'home_team',
        'away_team',
        'referee',
        'result'
    ]

    # Known before the match, so there is no leakage
    pre_match_date_attributes = [
        'weekday',
        'month'
    ]

    derived_attributes = [
        'home_points',
        'away_points',
        'home_indiscipline_index',
        'away_indiscipline_index',
        'total_indiscipline_index',
        'home_discipline_per_foul',
        'away_discipline_per_foul',
        'home_shot_efficiency',
        'away_shot_efficiency'
    ]

    raw_statistics = [
        'home_goals',
        'away_goals',
        'home_shots',
        'away_shots',
        'home_shots_on_target',
        'away_shots_on_target',
        'home_corners',
        'away_corners',
        'home_fouls',
        'away_fouls',
        'home_yellow_cards',
        'away_yellow_cards',
        'home_red_cards',
        'away_red_cards',
        'total_yellow_cards',
        'total_red_cards',
        'total_fouls',
        'total_goals'
    ]

    def has_statistic(column, statistics):
        return any(
            f'_{statistic}_avg_last' in column
            for statistic in statistics
        )

    disciplinary_windows = [
        column
        for column in base.columns
        if '_avg_last' in column
        and has_statistic(column, DISCIPLINARY_STATISTICS)
    ]

    performance_style_windows = [
        column
        for column in base.columns
        if '_avg_last' in column
        and not has_statistic(column, DISCIPLINARY_STATISTICS)
        and has_statistic(column, PERFORMANCE_STATISTICS)
    ]

    return {
        'identification': identification,
        'pre_match_date_attributes': pre_match_date_attributes,
        'current_match_attributes_DO_NOT_USE_IN_PREDICTIVE_MODEL':
            derived_attributes + raw_statistics,
        'disciplinary_windows': sorted(disciplinary_windows),
        'performance_style_windows': sorted(performance_style_windows)
    }


def save_column_categorization(categorization):
    """Saves the column categorization as JSON and returns its path."""

    CATEGORIZATION_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(CATEGORIZATION_FILE, 'w', encoding='utf-8') as file:
        json.dump(categorization, file, ensure_ascii=False, indent=4)

    return CATEGORIZATION_FILE


# MAIN FUNCTION
def calculate_rolling_windows(base_with_attributes):
    """
    Runs Step 5: adds the 3 to 7 match windows, checks for leakage and
    missing values, saves the column categorization and returns the base.
    """

    print('\n' + '=' * 70)
    print('STEP 5 - ROLLING WINDOWS OF HISTORICAL PERFORMANCE')
    print('=' * 70)

    team_history = build_team_history(base_with_attributes)

    print('\n[OK] Team history built.')
    print(f'Rows in the long history: {len(team_history)}')

    if len(team_history) == len(base_with_attributes) * 2:
        print('[OK] Each match produced two rows in the history.')
    else:
        print('[WARNING] The history does not have exactly two rows per match.')

    history_with_averages = calculate_rolling_averages(team_history)

    print('[OK] Historical averages of 3 to 7 matches computed.')

    final_base = merge_history_into_base(
        base_with_attributes,
        history_with_averages
    )

    print('[OK] Historical averages added to the original base.')

    check_data_leakage(base_with_attributes, team_history)

    missing_report = build_missing_report(final_base)

    categorization_path = save_column_categorization(
        build_column_categorization(final_base)
    )

    print(f'\n[OK] Column categorization saved to: {categorization_path}')

    print('\n' + '=' * 70)
    print('HISTORICAL WINDOWS SUMMARY')
    print('=' * 70)

    for window_size, summary in missing_report.items():
        print(
            f'last{window_size}: '
            f"{summary['rows_with_nan']} row(s) with NaN | "
            f"{summary['distinct_teams_affected']} team(s) affected"
        )

    return final_base


# RUN STEPS 4 AND 5 ON THEIR OWN
if __name__ == '__main__':

    # Imported here so main.py can still import this module from the
    # prepare package
    from step4_derived_attributes import calculate_derived_attributes

    print('\nLoading the clean base...')

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f'Input file not found: {INPUT_FILE}')

    clean_base = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')

    # The CSV stores dates as text
    clean_base['date'] = pd.to_datetime(clean_base['date'], errors='coerce')

    base_with_attributes = calculate_derived_attributes(clean_base)

    attributes_base = calculate_rolling_windows(base_with_attributes)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    attributes_base.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    new_window_columns = [
        column
        for column in attributes_base.columns
        if '_avg_last' in column
    ]

    print('\n' + '=' * 70)
    print('NEW WINDOW COLUMNS')
    print('=' * 70)

    print(f'Number of new window columns: {len(new_window_columns)}')

    for column in new_window_columns:
        print(f' - {column}')

    print('\n' + '=' * 70)
    print('STEP 5 - COMPLETED')
    print('=' * 70)

    print(
        f'Final base shape: '
        f'{len(attributes_base)} rows x '
        f'{len(attributes_base.columns)} columns'
    )

    print(f'\nFinal file saved to: {OUTPUT_FILE}')
    print(f'\n[OK] Categorization file saved to:\n{CATEGORIZATION_FILE.as_posix()}')

    print('=' * 70)
