import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
import os

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'liveData.csv')


def get_btc_data(limit=1000):
    url = 'https://min-api.cryptocompare.com/data/v2/histominute'
    params = {
        'fsym': 'BTC',
        'tsym': 'USD',
        'limit': limit,
        'aggregate': 5
    }
    response = requests.get(url, params=params)
    candles = response.json()['Data']['Data']

    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df[['time', 'open', 'high', 'low', 'close', 'volumeto']].rename(columns={
        'time': 'Timestamp',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volumeto': 'Volume'
    })
    return df


def write_to_csv(df):
    df.to_csv(CSV_FILE, mode='w', index=False)


def wait_until_next_run():
    now = datetime.now(timezone.utc)
    next_minute = (now.minute // 5 + 1) * 5

    if next_minute == 60:
        next_minute = 0
        next_hour = now.hour + 1
    else:
        next_hour = now.hour

    if next_hour == 24:
        next_hour = 0

    next_run_time = now.replace(hour=next_hour, minute=next_minute, second=5, microsecond=0)
    if next_run_time <= now:
        next_run_time += timedelta(minutes=5)

    wait_time = (next_run_time - now).total_seconds()
    return max(wait_time, 0)


# clears the file and writes all the new data
write_to_csv(get_btc_data(limit=1000))
print(f"CSV updated at {datetime.now(timezone.utc)}")

while True:
    wait_time = wait_until_next_run()

    # made a countdown timer
    while wait_time > 0:
        print(f"Next update in {int(wait_time)} seconds...", end='\r')
        time.sleep(1)
        wait_time -= 1

    write_to_csv(get_btc_data(limit=1000))
    print(f"\nCSV updated at {datetime.now(timezone.utc)}")

    next_wait_time = wait_until_next_run()
    print(f"Next update will happen in approximately {int(next_wait_time)} seconds.")
