# DATA AVAILABILITY ANALYSIS
import pandas as pd
from pathlib import Path


# SETTINGS
INPUT_FILE = Path('data/processed/unified_base.csv')

OUTPUT_FILE = Path('data/processed/clean_base.csv')

REPORT_FILE = Path('results/tables/availability_report.txt')


# MAIN STATISTICAL COLUMNS
STAT_COLUMNS = [
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
    'home_goals',
    'away_goals'
]

GOAL_COLUMNS = ['home_goals', 'away_goals']

# Columns shown when listing removed matches
MATCH_SUMMARY_COLUMNS = [
    'league',
    'season',
    'date',
    'home_team',
    'away_team',
    'home_goals',
    'away_goals'
]


def remove_empty_rows(unified_base):
    """
    Removes the rows identified as ghost records.

    A missing home_goals value is used as the criterion to
    identify the fully empty rows seen in the raw files.
    """

    rows_before = len(unified_base)

    clean_base = unified_base[unified_base['home_goals'].notna()].copy()

    removed_rows = rows_before - len(clean_base)

    print('\n' + '=' * 60)
    print('GHOST ROW REMOVAL')
    print('=' * 60)

    print(f'Rows before cleaning : {rows_before}')
    print(f'Rows removed         : {removed_rows}')
    print(f'Rows after cleaning  : {len(clean_base)}')

    return clean_base, removed_rows


def build_availability_report(base):
    """
    Computes the count and percentage of missing values for
    each column of the base.
    """

    total_rows = len(base)

    report = pd.DataFrame({
        'column': base.columns,
        'missing': base.isna().sum().values
    })

    if total_rows > 0:
        report['missing_pct'] = report['missing'] / total_rows * 100
    else:
        report['missing_pct'] = 0

    return report


def expected_matches(league, season):
    """
    Returns the expected number of matches for each league and
    season, given the known composition of the leagues.
    """

    # Bundesliga
    if league == 'D1':
        return 306

    # Ligue 1: 18 teams from 2023/2024 on; 2019/2020 ended early
    if league == 'F1':

        if season == '2019/2020':
            return 279

        if season in ['2023/2024', '2024/2025']:
            return 306

        return 380

    # Premier League, La Liga and Serie A
    return 380


def build_diagnostics(base):
    """
    Builds the diagnostics used to document the Step 3
    decisions:
    - referee availability per league and season;
    - number of matches per league and season, compared with
      the expected number.
    """

    referee_diagnostic = (
        base
        .groupby(['league', 'season'])
        .agg(
            total_matches=('league', 'size'),
            missing_referees=('referee', lambda column: column.isna().sum())
        )
        .reset_index()
    )

    referee_diagnostic['present_referees'] = (
        referee_diagnostic['total_matches']
        - referee_diagnostic['missing_referees']
    )

    referee_diagnostic['present_referees_pct'] = (
        referee_diagnostic['present_referees']
        / referee_diagnostic['total_matches']
        * 100
    )

    match_counts = (
        base
        .groupby(['league', 'season'])
        .size()
        .reset_index(name='matches')
    )

    match_counts['expected'] = match_counts.apply(
        lambda row: expected_matches(row['league'], row['season']),
        axis=1
    )

    match_counts['difference'] = match_counts['matches'] - match_counts['expected']

    match_counts['status'] = (
        match_counts['matches'] == match_counts['expected']
    ).map({
        True: 'OK',
        False: 'OUT OF PATTERN'
    })

    return referee_diagnostic, match_counts


def remove_matches_without_stats(base):
    """
    Removes real matches with no information in any of the
    statistical variables of interest.

    Goals are left out of this criterion, since the identified
    matches do have goals and result. A match is removed only
    when all the other statistical variables are missing at once.
    """

    columns_to_check = [
        column
        for column in STAT_COLUMNS
        if column not in GOAL_COLUMNS
    ]

    without_stats_mask = base[columns_to_check].isna().all(axis=1)

    removed_matches = base[without_stats_mask].copy()

    print('\n' + '=' * 60)
    print('REMOVAL OF MATCHES WITHOUT STATISTICS')
    print('=' * 60)

    print(f'Matches identified for removal: {len(removed_matches)}')

    if len(removed_matches) > 0:

        print('\nRemoved matches:')
        print(removed_matches[MATCH_SUMMARY_COLUMNS].to_string(index=False))

    else:
        print('No match without statistics was found.')

    clean_base = base[~without_stats_mask].copy()

    print(f'\nRows before removal: {len(base)}')
    print(f'Rows after removal: {len(clean_base)}')

    return clean_base, removed_matches


def check_missing_stats(base):
    """
    Finds records that still have missing values in the main
    statistical columns of the study.

    The rows found are not removed at this step.
    """

    existing_columns = [
        column
        for column in STAT_COLUMNS
        if column in base.columns
    ]

    missing_mask = base[existing_columns].isna()

    rows_with_missing = base[missing_mask.any(axis=1)].copy()

    missing_per_column = missing_mask.sum()

    return missing_per_column, rows_with_missing


def build_report_text(
    base_before,
    base_after,
    report_before,
    report_after,
    referee_diagnostic,
    match_counts,
    ghost_rows_removed,
    matches_without_stats,
    missing_stats,
    rows_with_missing
):
    """
    Builds the full Step 3 text report, recording the numbers,
    diagnostics and methodological decisions of this step.
    """

    lines = []

    def add_section(title):
        lines.append('=' * 80)
        lines.append(title)
        lines.append('=' * 80)
        lines.append('')

    def format_availability(report):
        return report.to_string(
            index=False,
            formatters={'missing_pct': '{:.2f}%'.format}
        )

    rows_after_ghosts = len(base_before) - ghost_rows_removed

    add_section('DATA AVAILABILITY REPORT - STEP 3')
    lines.append(
        'This report documents the data availability analysis of the '
        'unified base and the cleaning decisions made in Step 3 of the '
        'project.'
    )
    lines.append('')

    add_section('1. GHOST ROW CLEANING')
    lines.append(f'Original rows: {len(base_before)}')
    lines.append(f'Rows removed as ghosts: {ghost_rows_removed}')
    lines.append(f'Rows after removing ghosts: {rows_after_ghosts}')
    lines.append('')
    lines.append(
        'The rows identified as ghost records in the original CSV files '
        'were removed. The operational criterion used was a missing '
        'home_goals value, as found in the inspection done in the '
        'previous step.'
    )
    lines.append('')

    add_section('2. REMOVAL OF REAL MATCHES WITHOUT STATISTICS')
    lines.append(f'Real matches removed: {len(matches_without_stats)}')
    lines.append('')

    if len(matches_without_stats) > 0:
        lines.append('Removed matches:')
        lines.append(
            matches_without_stats[MATCH_SUMMARY_COLUMNS].to_string(index=False)
        )
        lines.append('')

    lines.append(
        'The decision to remove these matches was made because the impact '
        'is statistically negligible: 2 out of 18,011 rows, equivalent '
        'to roughly 0.011% of the base after removing the ghost rows.'
    )
    lines.append('')
    lines.append(
        'These variables are central to the study, especially cards '
        'and fouls. No mean, median or zero imputation was used, '
        'since any of these alternatives would introduce an assumption '
        'about the discipline level of the matches without observed '
        'information that could methodologically support it.'
    )
    lines.append('')
    lines.append(
        'Furthermore, keeping missing values in these matches could '
        'propagate the problem to Step 4, especially when building the '
        'sliding windows of 3 to 7 matches, where missing values in the '
        'middle of the window could prevent or distort the calculation '
        'of the historical features.'
    )
    lines.append('')
    lines.append(
        'Therefore, the two real matches without statistics were removed, '
        'without imputing the missing values.'
    )
    lines.append('')

    add_section('3. DATA AVAILABILITY - BEFORE CLEANING')
    lines.append(format_availability(report_before))
    lines.append('')

    add_section('4. DATA AVAILABILITY - AFTER CLEANING')
    lines.append(format_availability(report_after))
    lines.append('')

    add_section('5. REFEREE VARIABLE AVAILABILITY')
    lines.append(
        "The 'referee' column was kept in the base, but it will not be "
        'used as a feature of the machine learning model.'
    )
    lines.append('')
    lines.append(
        'The source analysis showed that referee data is available only '
        'for the Premier League (E0). For D1, F1, I1 and SP1, the column '
        'is not present in the raw files of these leagues. Therefore, '
        'these gaps are a limitation of the source availability, and not '
        'individual values that could be imputed.'
    )
    lines.append('')
    lines.append(
        referee_diagnostic.to_string(
            index=False,
            formatters={'present_referees_pct': '{:.2f}%'.format}
        )
    )
    lines.append('')
    lines.append(
        "Methodological decision: the 'referee' variable will not be used "
        'as a model feature, since its availability is restricted to a '
        'single league. The column stays in the clean base to preserve '
        'the original information from the source.'
    )
    lines.append('')

    add_section('6. NUMBER OF MATCHES PER LEAGUE AND SEASON')
    lines.append(match_counts.to_string(index=False))
    lines.append('')
    lines.append(
        'The number of matches is compared with the expected number '
        'for each league composition.'
    )
    lines.append('')
    lines.append(
        'The F1 2019/2020 season has 279 matches. This number is not '
        'treated as a reading error, since the season was interrupted '
        'and ended early due to the Covid-19 pandemic.'
    )
    lines.append('')
    lines.append(
        "The French Conseil d'État records that, due to the Covid-19 "
        'epidemic, the Ligue de Football Professionnel (LFP) decided '
        'on April 30, 2020 to definitively end the 2019/2020 season '
        'of Ligue 1 and Ligue 2. The decision took into account the '
        'health context and the impossibility of resuming the '
        'competitions under the conditions existing at the time.'
    )
    lines.append('')
    lines.append(
        "Main source: Conseil d'État, decision of June 9, 2020, "
        "\"Ligue 1 de football : le juge des référés du Conseil d'État "
        'valide la fin de la saison et le classement mais suspend les '
        'relégations".'
    )
    lines.append(
        'https://conseil-etat.fr/actualites/'
        'ligue-1-de-football-le-juge-des-referes-du-conseil-d-etat-'
        'valide-la-fin-de-la-saison-et-le-classement-mais-suspend-les-relegations'
    )
    lines.append('')

    add_section('7. REMAINING GAPS IN THE STATISTICAL VARIABLES')

    if len(rows_with_missing) == 0:
        lines.append(
            'No missing values were found in the statistical columns '
            'after removing the ghost rows.'
        )
    else:
        lines.append(
            'Missing values were found after cleaning. None of these '
            'rows was removed automatically at this step.'
        )
        lines.append('')
        lines.append('Missing values per column:')
        lines.append(missing_stats[missing_stats > 0].to_string())
        lines.append('')
        lines.append('Full rows with missing values:')
        lines.append(rows_with_missing.to_string(index=False))

    lines.append('')

    add_section('8. CLEAN BASE')
    lines.append(f'Original rows: {len(base_before)}')
    lines.append(f'After removing ghost rows: {rows_after_ghosts}')
    lines.append(f'After removing matches without statistics: {len(base_after)}')
    lines.append(f'Rows removed as ghosts: {ghost_rows_removed}')
    lines.append(
        f'Real matches without statistics removed: {len(matches_without_stats)}'
    )
    lines.append('')
    lines.append('Columns of the final base:')
    lines.extend(f'- {column}' for column in base_after.columns)
    lines.append('')
    lines.append(
        "The 'referee' column stays in the final base, although it is "
        'not used as a model feature.'
    )
    lines.append('')

    add_section('9. HANDOFF TO STEP 4')
    lines.append(
        'The clean base saved to data/processed/clean_base.csv '
        'is the input for the next step of the project.'
    )
    lines.append(
        'Decisions about any remaining statistical gaps were not made '
        'automatically when incomplete records were found; these rows '
        'were only documented for methodological review.'
    )
    lines.append('')

    return '\n'.join(lines)


# MAIN PROGRAM
def analyze_availability(unified_base):
    """
    Runs the Step 3 availability analysis.

    Removes only the identified ghost rows and the matches
    without statistics, builds the availability reports before
    and after cleaning, documents the referee limitation, checks
    the number of matches per league and season, records any
    remaining statistical gaps and saves the clean base and the
    text report.

    Returns the clean DataFrame so it can be chained with the
    next steps of the project.
    """

    print('=' * 60)
    print('STEP 3 - AVAILABILITY ANALYSIS')
    print('=' * 60)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    report_before = build_availability_report(unified_base)

    clean_base, ghost_rows_removed = remove_empty_rows(unified_base)

    clean_base, matches_without_stats = remove_matches_without_stats(clean_base)

    report_after = build_availability_report(clean_base)

    referee_diagnostic, match_counts = build_diagnostics(clean_base)

    # Checked only after both removals
    missing_stats, rows_with_missing = check_missing_stats(clean_base)

    report_text = build_report_text(
        unified_base,
        clean_base,
        report_before,
        report_after,
        referee_diagnostic,
        match_counts,
        ghost_rows_removed,
        matches_without_stats,
        missing_stats,
        rows_with_missing
    )

    print('\n' + report_text)

    REPORT_FILE.write_text(report_text, encoding='utf-8')

    clean_base.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    print('\n' + '=' * 60)
    print('STEP 3 COMPLETED')
    print('=' * 60)
    print(f'Clean base saved to: {OUTPUT_FILE}')
    print(f'Report saved to: {REPORT_FILE}')

    return clean_base


# RUN THE STEP ON ITS OWN
if __name__ == '__main__':

    if not INPUT_FILE.exists():

        print(f'[ERROR] Input file not found: {INPUT_FILE}')

    else:

        unified_base = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')

        analyze_availability(unified_base)
