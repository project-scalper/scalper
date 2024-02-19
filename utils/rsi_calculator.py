#!/usr/bin/python3

import pandas_ta as ta
import pandas as pd
from datetime import datetime, timedelta
from typing import List
import ccxt
import asyncio

async def rsi(exchange:ccxt.Exchange, symbol:str, timeframe:str='5m', rsi_length:int=6, ohlcv:List=None):
    """Relative Strength Index of a  symbol
    Args:
        exchange: A ccxt exchange instance
        symbol: The unified symbol of the token eg BTC/USDT
        timeframe: Can be any of the following; 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        rsi_length: The number of candles over which rsi should be calculated
    Return:
        A list of dicts containing three instances of open, high, low, close, volume, RSI, datetime"""
    try:
        if not ohlcv:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
        if len(ohlcv):
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            # df['time'] = pd.to_datetime(df['time'], unit='ms')
            df = pd.concat([df, df.ta.rsi(length=rsi_length)], axis=1)
            resp = df.tail(5).to_dict(orient='records')
            for item in resp:
                item['datetime'] = datetime.fromtimestamp(item['time'] / 1000)

            resp.reverse()
            last_close = datetime.now() - timedelta(minutes=5)
            if resp[0]['datetime'] > last_close:
                resp.pop(0)
            return resp

    except Exception as e:
        print(type(e).__name__, str(e))


async def main():
    from exchange import bybit as exchange
    resp = await rsi(exchange, "DOGE/USDT", timeframe='5m', rsi_length=6)
    print(resp)
    # await exchange.close()
    
if __name__ == '__main__':
    asyncio.run(main())