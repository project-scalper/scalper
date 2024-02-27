#!/usr/bin/python3

from utils.ema_calculator import ema
from utils.macd_calculator import macd
from utils.rsi_calculator import rsi
# from utils import get_indicators
# from exchange import bybit as exchange
from strategies.checker import Checker
import threading
# from typing import Dict, List
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe, exchange
import asyncio
import ccxt


def start_checker(symbol, signal):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(new_checker(symbol, signal))

async def run_thread(symbol, sig_type):
    nt = threading.Thread(target=start_checker, args=(symbol, sig_type))
    nt.start()

async def new_checker(symbol, sig_type):
    trade = Checker()
    await trade.execute(symbol, sig_type)
    trade.delete()


async def analyser(symbol:str, exchange:ccxt.Exchange)-> None:
    ema_50, ema_200, _macd, _rsi = await asyncio.gather(ema(exchange, symbol, 50, timeframe),
                                                        ema(exchange, symbol, 200, timeframe),
                                                        macd(exchange, symbol, timeframe),
                                                        rsi(exchange, symbol, timeframe))
    
    if not ema_50 or not ema_200 or not _macd or not _rsi:
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return

    # keys
    # 0 - NEUTRAL
    # 1 - EXISTING_BUY
    # 2 - FRESH_BUY
    # -1 - EXISTING_SELL
    # -2 - FRESH_SELL
    flags = {"EMA": 0, "MACD": 0, "RSI": 0}

    # check EMA values
    if ema_50[0]['EMA_50'] > ema_200[0]['EMA_200']:
        if ema_50[1]['EMA_50'] <= ema_200[1]['EMA_200']:
            flags['EMA'] = 2
        else:
            flags['EMA'] = 1
    elif ema_50[0]['EMA_50'] < ema_200[0]['EMA_200']:
        if ema_50[1]['EMA_50'] >= ema_200[1]['EMA_200']:
            flags['EMA'] = -2
        else:
            flags['EMA'] = -1

    # Confirm with MACD value
    signal = watchlist.get(symbol)
    if _macd[0]['MACDh_12_26_9'] > 0:
        if _macd[1]['MACDh_12_26_9'] <= 0:
            flags['MACD'] = 2
        else:
            flags['MACD'] = 1
    if _macd[0]['MACDh_12_26_9'] < 0:
        if _macd[1]['MACDh_12_26_9'] >= 0:
            flags['MACD'] = -2
        else:
            flags['MACD'] = -1

    sig_type = None
    if flags['EMA'] == 2:
        if flags['MACD'] == 2:
            sig_type = 'EMA/MACD_BUY'
        elif flags['MACD'] == 1:
            sig_type = 'EMA_MACD_BUY'
        else:
            sig_type = 'NEUTRAL'
    if flags['MACD'] == 2:
        if flags['EMA'] == 1:
            sig_type = 'MACD_EMA_BUY'
        else:
            sig_type = 'NEUTRAL'


    if flags['EMA'] == -2:
        if flags['MACD'] == -2:
            sig_type = 'EMA/MACD_SELL'
        elif flags['MACD'] == -1:
            sig_type = "EMA_MACD_SELL"
        else:
            sig_type = "NEUTRAL"
    if flags['MACD'] == -2:
        if flags['EMA'] == -1:
            sig_type = "MACD_EMA_SELL"
        else:
            sig_type = 'NEUTRAL'

    if sig_type is not None:
        watchlist.put(symbol, sig_type)

    # confirm with rsi
    signal = watchlist.get(symbol)
    if "BUY" in signal:
        if _rsi[0]['RSI_6'] > 70:
            watchlist.reset(symbol)
    if "SELL" in signal:
        if _rsi[0]['RSI_6'] < 30:
            watchlist.reset(symbol)

    if sig_type and watchlist.get(symbol) != "NEUTRAL":
        await run_thread(symbol, sig_type)
        

async def main():
    print("Loading markets...")
    exchange.load_markets()
    symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'WAVES/USDT', 'ETC/USDT']
    tasks = [analyser(symbol, exchange) for symbol in symbols]
    await asyncio.gather(*tasks)
    all_sym = watchlist.get_all()
    adapter.info(all_sym)
    
if __name__ == '__main__':
    asyncio.run(main())
