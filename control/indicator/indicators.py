import pandas as pd
import numpy as np
import json
from django.conf import settings
from pybit.unified_trading import HTTP

# API 설정 읽기
api_key = settings.API_KEY
api_secret = settings.API_SECRET

# HTTP 세션 초기화
session = HTTP(api_key=api_key, api_secret=api_secret)

# DataFrame 초기화
df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# 기술적 지표 계산 함수
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta > 0) * delta
    loss = (delta < 0) * -delta
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, slow=26, fast=12, signal=9):
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger_bands(data, window=20):
    ma = data.rolling(window=window).mean()
    sd = data.rolling(window=window).std()
    return ma + 2 * sd, ma - 2 * sd

# 웹소켓 메시지 처리
def on_message(ws, message):
    global df
    try:
        data = json.loads(message)
        if 'data' in data and data['data'][0].get('confirm', False):
            kline_data = data['data'][0]
            new_row = {
                'timestamp': pd.to_datetime(kline_data['start'], unit='ms'),
                'open': float(kline_data['open']),
                'high': float(kline_data['high']),
                'low': float(kline_data['low']),
                'close': float(kline_data['close']),
                'volume': float(kline_data['volume'])
            }
            df = df.append(new_row, ignore_index=True)

            df['RSI'] = calculate_rsi(df['close'])
            df['MACD'], df['Signal_Line'] = calculate_macd(df['close'])
            df['Upper_Band'], df['Lower_Band'] = calculate_bollinger_bands(df['close'])
    except Exception as e:
        print(f"Error processing message: {e}")