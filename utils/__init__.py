#!/usr/bin/python3

# from utils.ema_calculator import ema
# from utils.macd_calculator import macd
# from utils.rsi_calculator import rsi
# from exchange import bybit as exchange
# from variables import timeframe, exchange
# import asyncio


# def get_indicators(symbol:str):
#     ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
#     tasks = [ema(exchange, symbol, 50, timeframe, ohlcv=ohlcv),
#                 ema(exchange, symbol, 200, timeframe, ohlcv=ohlcv),
#                 macd(exchange, symbol, timeframe, ohlcv=ohlcv),
#                 rsi(exchange, symbol, timeframe, ohlcv=ohlcv)]
#     indicators = asyncio.gather(*tasks)
#     return indicators
