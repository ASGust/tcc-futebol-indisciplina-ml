# DATA DOWNLOAD
import requests
from pathlib import Path


# SETTINGS
LEAGUES = [
    'E0',   # Premier League
    'SP1',  # La Liga
    'I1',   # Serie A
    'D1',   # Bundesliga
    'F1'    # Ligue 1
]

# Seasons 2015/2016 to 2024/2025
SEASONS = [
    '1516',
    '1617',
    '1718',
    '1819',
    '1920',
    '2021',
    '2122',
    '2223',
    '2324',
    '2425'
]

BASE_URL = 'https://www.football-data.co.uk/mmz4281'

RAW_DATA_DIR = Path('data/raw')


# MAIN PROGRAM
def download_all_files():
    """
    Downloads the CSV of every league and season, skipping cached files.
    Returns the download counts so main.py can decide whether to go on.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    downloaded_count = 0
    cached_count = 0
    failed_count = 0

    for season in SEASONS:

        for league in LEAGUES:

            file_name = f'{league}_{season}.csv'
            file_path = RAW_DATA_DIR / file_name

            if file_path.exists():
                print(f'[CACHE] {file_name} already exists.')
                cached_count += 1
                continue

            url = f'{BASE_URL}/{season}/{league}.csv'

            print(f'[DOWNLOAD] Downloading {file_name}...')

            try:

                response = requests.get(url, timeout=30)

                # Raises on HTTP errors such as 404 or 500
                response.raise_for_status()

                if not response.content:
                    raise ValueError('The returned file is empty.')

                file_path.write_bytes(response.content)

                print(f'[OK] {file_name} downloaded successfully.')
                downloaded_count += 1

            except requests.exceptions.RequestException as error:

                print(f'[ERROR] Failed to download {file_name}: {error}')
                failed_count += 1

            except Exception as error:

                print(f'[ERROR] Problem saving {file_name}: {error}')
                failed_count += 1

    # FINAL SUMMARY
    print('\n' + '=' * 60)
    print('DOWNLOAD SUMMARY')
    print('=' * 60)

    print(f'Files downloaded now : {downloaded_count}')
    print(f'Files already cached : {cached_count}')
    print(f'Files failed         : {failed_count}')
    print('=' * 60)

    return {
        'downloaded': downloaded_count,
        'cached': cached_count,
        'failed': failed_count
    }


# RUN THE PROGRAM
if __name__ == '__main__':
    download_all_files()
