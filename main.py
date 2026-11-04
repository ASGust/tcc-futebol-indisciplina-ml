# FULL PROJECT PIPELINE
# Chains Steps 1 to 6; each step only runs if the previous one succeeded.
# Run from the project root: python main.py
import sys

from prepare.step1_download import download_all_files
from prepare.step2_unification import unify_files
from prepare.step3_availability import analyze_availability
from prepare.step4_derived_attributes import calculate_derived_attributes
from prepare.step5_rolling_windows import (
    calculate_rolling_windows,
    OUTPUT_FILE as ATTRIBUTES_BASE_FILE,
    CATEGORIZATION_FILE
)
from prepare.step6_final_selection import (
    select_final_columns,
    OUTPUT_FILE as FINAL_BASE_FILE
)


def stop_pipeline(message):
    """Reports where the pipeline stopped and exits with an error code."""

    print(f'\n[main] [ERROR] {message}')
    print('[main] Pipeline stopped.')

    sys.exit(1)


# MAIN PROGRAM
def main():

    # STEP 1 - DOWNLOAD
    print('\n[main] Step 1/6: download...')

    download_summary = download_all_files()

    # Nothing to unify without downloaded or cached files
    if download_summary['downloaded'] + download_summary['cached'] == 0:
        stop_pipeline('No CSV file available (0 downloaded and 0 cached).')

    # STEP 2 - UNIFICATION
    print('\n[main] Step 2/6: unification...')

    unified_base = unify_files()

    if unified_base is None:
        stop_pipeline(
            'Unification produced no base (no CSV found '
            'or none could be processed).'
        )

    # STEP 3 - AVAILABILITY AND CLEANING
    print('\n[main] Step 3/6: availability and cleaning...')

    try:
        clean_base = analyze_availability(unified_base)

    except Exception as error:
        stop_pipeline(f'Step 3 failed: {error}')

    # STEP 4 - DERIVED ATTRIBUTES
    print('\n[main] Step 4/6: derived attributes...')

    try:
        base_with_attributes = calculate_derived_attributes(clean_base)

    except Exception as error:
        stop_pipeline(f'Step 4 failed: {error}')

    # STEP 5 - ROLLING WINDOWS
    print('\n[main] Step 5/6: rolling windows...')

    try:
        # Also saves the column categorization
        attributes_base = calculate_rolling_windows(base_with_attributes)

        # Step 5 does not save the attributes base itself, so it is
        # saved here with the step's file name and encoding
        ATTRIBUTES_BASE_FILE.parent.mkdir(parents=True, exist_ok=True)

        attributes_base.to_csv(
            ATTRIBUTES_BASE_FILE,
            index=False,
            encoding='utf-8-sig'
        )

    except Exception as error:
        stop_pipeline(f'Step 5 failed: {error}')

    # STEP 6 - FINAL COLUMN SELECTION
    print('\n[main] Step 6/6: final column selection...')

    try:
        final_base = select_final_columns(attributes_base)

    except Exception as error:
        stop_pipeline(f'Step 6 failed: {error}')

    # FINAL SUMMARY
    print('\n' + '=' * 70)
    print('[main] PIPELINE COMPLETED')
    print('=' * 70)

    print(
        f'Final base dimensions: '
        f'{len(final_base)} rows x '
        f'{len(final_base.columns)} columns'
    )

    print('\nMain files generated:')
    print(f' - {ATTRIBUTES_BASE_FILE.as_posix()}')
    print(f' - {CATEGORIZATION_FILE.as_posix()}')
    print(f' - {FINAL_BASE_FILE.as_posix()}')
    print('=' * 70)


# RUN THE PIPELINE
if __name__ == '__main__':
    main()
