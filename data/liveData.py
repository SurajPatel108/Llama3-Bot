import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
import os

x = 0

DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(DATA_FOLDER, 'liveData.csv')

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def get_btc_data(limit=1000):
    url = 'https://min-api.cryptocompare.com/data/v2/histominute'
    params = {
        'fsym': 'BTC',
        'tsym': 'USD',
        'limit': limit,
        'aggregate': 5
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'Data' not in data or 'Data' not in data['Data'] or len(data['Data']['Data']) == 0:
        raise ValueError("Unexpected data format or no data found in response")

    candles = data['Data']['Data']
    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df[['time', 'open', 'high', 'low', 'close', 'volumeto']]
    df.rename(columns={
        'time': 'Timestamp', 
        'open': 'Open', 
        'high': 'High', 
        'low': 'Low', 
        'close': 'Close', 
        'volumeto': 'Volume'
    }, inplace=True)
    
    return df

def write_to_csv(df):
    df.to_csv(CSV_FILE, mode='w', index=False)

def get_latest_btc_5min_data():
    url = 'https://min-api.cryptocompare.com/data/v2/histominute'
    params = {
        'fsym': 'BTC',
        'tsym': 'USD',
        'limit': 1,
        'aggregate': 5
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'Data' not in data or 'Data' not in data['Data'] or len(data['Data']['Data']) == 0:
        raise ValueError("Unexpected data format or no data found in response")
    
    candles = data['Data']['Data']
    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    latest_data = df[['time', 'open', 'high', 'low', 'close', 'volumeto']].rename(columns={
        'time': 'Timestamp', 
        'open': 'Open', 
        'high': 'High', 
        'low': 'Low', 
        'close': 'Close', 
        'volumeto': 'Volume'
    }).iloc[-1]
    
    return latest_data.to_frame().T

def wait_until_next_run():
    now = datetime.now(timezone.utc)
    current_minute = now.minute
    next_run_minute = (current_minute // 5 + 1) * 5
    
    if next_run_minute == 60:
        next_run_minute = 0
        next_run_hour = now.hour + 1
    else:
        next_run_hour = now.hour
    
    if next_run_hour == 24:
        next_run_hour = 0
    
    try:
        next_run_time = now.replace(hour=next_run_hour, minute=next_run_minute, second=5, microsecond=0)
    except ValueError as e:
        print(f"ValueError: {e}")
        next_run_time = now.replace(minute=0, second=5, microsecond=0) + timedelta(hours=1)
    
    if next_run_time <= now:
        next_run_time += timedelta(minutes=5)
    
    wait_time = (next_run_time - now).total_seconds()
    
    return wait_time

initial_data = get_btc_data(limit=1000)
write_to_csv(initial_data)

while True:
    wait_time = wait_until_next_run()
    print(f"Waiting for {wait_time:.2f} seconds...")
    time.sleep(wait_time)
    latest_data = get_latest_btc_5min_data()
    write_to_csv(latest_data)
    print(f"Updated CSV with new row: {latest_data.to_dict(orient='records')[0]}")
    x+=1