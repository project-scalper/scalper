#!/usr/bin/python3

import pandas_ta as ta
import pandas as pd
from helper.adapter import adapter
import asyncio
import time
from datetime import datetime, timedelta
from typing import List


import ccxt  # noqa: E402


async def ema(exchange:ccxt.Exchange, symbol:str, length:int, timeframe:str='5m', ohlcv:List=None) -> List:
    """Exponential Moving Average of a symbol.
    Args:
        exchange: A ccxt exchange instance
        symbol: The unified symbol of the token eg BTC/USDT
        length: the range over which the ema should be calculated
        timeframe: Can be any of the following; 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    Returns:
        A list of dicts containing three instances of open, high, low, close, volume, EMA, datetime
    """
    try:
        if not ohlcv:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
        if len(ohlcv):
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            # df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            ema = df.ta.ema(length)
            df = pd.concat([df, ema], axis=1)
            df = df.tail(5)
            resp = df.to_dict(orient='records')
            for item in resp:
                item['datetime'] = datetime.fromtimestamp(item['timestamp'] / 1000)
                key = f"EMA_{length}"
                item["EMA"] = item[key]
            resp.reverse()
            # ts = time.time() * 1000
            last_close = datetime.now() - timedelta(minutes=5)
            # print(last_close)
            if resp[0]['datetime'] > last_close:
                resp.pop(0)
            return resp
    except Exception as e:
        msg = f"{type(e).__name__} - {str(e)}"
        adapter.error(msg)


async def main():
    from exchange import bybit as exchange
    symbol = 'SOL/USDT:USDT'
    resp = await ema(exchange, symbol, 100)
    print(resp)

if __name__ == '__main__':
    asyncio.run(main())
