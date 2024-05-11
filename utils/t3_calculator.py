#!/usr/bin/python3

import pandas_ta as ta
import pandas as pd
from helper.adapter import adapter
import asyncio
import math
from datetime import datetime
from typing import List
from datetime import datetime, timedelta


import ccxt  # noqa: E402


async def t3(exchange:ccxt.Exchange, symbol:str, timeframe:str='5m', ohlcv:List=None) -> List:
    """Parabolic stop and reverse of a symbol.
    Args:
        exchange: A ccxt exchange instance
        symbol: The unified symbol of the token eg BTC/USDT
        timeframe: Can be any of the following; 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    Returns:
        A list of dicts containing three instances of open, high, low, close, volume, EMA, datetime
    """
    try:
        if not ohlcv:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=800)
        if len(ohlcv):
            fast_length = 45
            fast_a = 0.7
            slow_length = 180
            slow_a = 0.6
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            fast_t3 = df.ta.t3(length=fast_length, a=fast_a)
            slow_t3 = df.ta.t3(length=slow_length, a=slow_a)
            df = pd.concat([df, fast_t3], axis=1)
            df = pd.concat([df, slow_t3], axis=1)
            df = df.tail(10)
            resp = df.to_dict(orient='records')
            for item in resp:
                item['datetime'] = datetime.fromtimestamp(item['timestamp'] / 1000)
                item['FAST_T3'] = item[f"T3_{fast_length}_{fast_a}"]
                item['SLOW_T3'] = item[f'T3_{slow_length}_{slow_a}']
            resp.reverse()
            if datetime.now() - timedelta(minutes=5) > resp[0]['datetime']:
                return resp
            resp.pop(0)
            return resp
    except Exception as e:
        msg = f"{type(e).__name__} - {str(e)}"
        adapter.error(msg)


async def main():
    # from variables import exchange
    exchange = ccxt.huobi()
    exchange.nonce = ccxt.Exchange.milliseconds
    mkt = exchange.load_markets()
    symbol = 'ADA/USDT:USDT'
    resp = await t3(exchange, symbol, timeframe='5m')
    print(resp)

if __name__ == '__main__':
    asyncio.run(main())
