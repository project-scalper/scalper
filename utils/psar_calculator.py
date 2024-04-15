#!/usr/bin/python3

import pandas_ta as ta
import pandas as pd
from helper.adapter import adapter
import asyncio
import math
from datetime import datetime, timedelta
from typing import List


import ccxt  # noqa: E402


async def psar(exchange:ccxt.Exchange, symbol:str, timeframe:str='5m', ohlcv:List=None) -> List:
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
            af0 = 0.02
            af = 0.02
            max_af = 0.2
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            psar = df.ta.psar(af0=af0, af=af, max_af=max_af)
            df = pd.concat([df, psar], axis=1)
            df = df.tail(10)
            resp = df.to_dict(orient='records')
            for item in resp:
                item['datetime'] = datetime.fromtimestamp(item['timestamp'] / 1000)
                key = f"PSARs_{af0}_{max_af}"
                key2 = f"PSARl_{af0}_{max_af}"
                if not math.isnan(item[key]):
                    item["PSAR"] = item[key]
                elif not math.isnan(item[key2]):
                    item["PSAR"] = item[key2]
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
    symbol = 'SOL/USDT:USDT'
    resp = await psar(exchange, symbol, timeframe='5m')
    print(resp)

if __name__ == '__main__':
    asyncio.run(main())
