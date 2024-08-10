#!/usr/bin/python3

import pandas_ta as ta
import pandas as pd
import asyncio
from datetime import timedelta
from datetime import datetime
from variables import timeframe


import ccxt  # noqa: E402


async def bbands(exchange:ccxt.Exchange, symbol:str, length:int=20, ohlcv=None):
    """Obtains the Bollinger band values for a symbol
    Args:
        exchange: The ccxt exchange instance
        symbol: A unified base and quote string of the token eg 'BTC/USDT'
        length: Number of candles on which to calculate bband
        timeframe: Can be any of the following; 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    Returns:
        A list of dicts containing three instances of open, high, low, close, volume, BBAND, datetime"""
    
    if not ohlcv:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=500)

    std = 2.0
    if len(ohlcv):
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        bband = df.ta.bbands(length, std=std)
        df = pd.concat([df, bband], axis=1)
        df = df.tail(10)
        resp = df.to_dict(orient='records')
        for item in resp:
            item['datetime'] = datetime.fromtimestamp(item['timestamp'] / 1000)
            item['UPPER'] = item[f'BBU_{length}_{std}']
            item['MIDDLE'] = item[f'BBM_{length}_{std}']
            item['LOWER'] = item[f'BBL_{length}_{std}']
        resp.reverse()
        if datetime.now() - timedelta(minutes=5) > resp[0]['datetime']:
            return resp
        resp.pop(0)
        return resp


async def main():
    from exchange import bybit as exchange
    market = await exchange.load_markets()
    symbol = 'WAVES/USDT'
    resp = await bbands(exchange, symbol, 20)
    print(resp)
    # await exchange.close()

# asyncio.run(main())