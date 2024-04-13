#!/usr/bin/python3

import pandas_ta as ta
import pandas as pd
from helper.adapter import adapter
import asyncio
import math
from datetime import datetime
from typing import List


import ccxt  # noqa: E402


async def adx(exchange:ccxt.Exchange, symbol:str, timeframe:str='5m', ohlcv:List=None) -> List:
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
            length = 14
            lensig = length
            scalar = 100
            mamode = 'rma'
            drift = 1
            offset = 0
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            psar = df.ta.adx(length=length, scalar=scalar, lensig=lensig, mamode=mamode, drift=drift,
                             offset=offset)
            df = pd.concat([df, psar], axis=1)
            df = df.tail(10)
            resp = df.to_dict(orient='records')
            for item in resp:
                item['datetime'] = datetime.fromtimestamp(item['timestamp'] / 1000)
                item['ADX'] = item[f"ADX_{length}"]
                item['DMP'] = item[f'DMP_{length}']
                item['DMN'] = item[f'DMN_{length}']
            resp.reverse()
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
    symbol = 'SOL/USDT:USDT'
    resp = await adx(exchange, symbol, timeframe='5m')
    print(resp)

if __name__ == '__main__':
    asyncio.run(main())
