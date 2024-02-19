#!/usr/bin/python3

from asyncio import run
import pandas_ta as ta
import pandas as pd
from typing import List
from helper.adapter import adapter
from datetime import datetime, timedelta


import ccxt  # noqa: E402

async def macd(exchange:ccxt.Exchange, symbol:str, timeframe:str='5m', limit:int=200, ohlcv:List=None):
   since = None
   fast = 12
   slow = 26
   signal = 9
   try:
      if not ohlcv:
         ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
      if len(ohlcv):
         df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

         macd = df.ta.macd(fast=fast, slow=slow, signal=signal)
         df = pd.concat([df, macd], axis=1)
         df = df[-signal:]
         resp = df.tail(5).to_dict(orient='records')
         # print(resp)
         for item in resp:
            item['datetime'] = datetime.fromtimestamp(item['time'] / 1000)
         resp.reverse()
         # print(datetime.now())
         last_close = datetime.now() - timedelta(minutes=5)
         if resp[0]['datetime'] > last_close:
            resp.pop(0)
         return resp
   except Exception as e:
      msg = f"{type(e).__name__} {str(e)}"
      adapter.error(msg)


async def main():
   # from exchange import bybit as exchange
   exchange = ccxt.binance()
   timeframe = '5m'
   limit = 50
   resp = await macd(exchange, "SOL/USDT", timeframe, limit)
   print(resp)

if __name__ == '__main__':
   run(main())