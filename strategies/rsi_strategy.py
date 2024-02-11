#!/usr/bin/python3

from utils.ema_calculator import ema
from utils.macd_calculator import macd
from utils.rsi_calculator import rsi
from exchange import bybit as exchange
from strategies.checker import Checker
import threading
from typing import Dict, List
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe
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
    trade = Checker(symbol, signal=sig_type)
    await trade.execute()


async def analyser(symbol:str, exchange:ccxt.Exchange)-> None:
    ema_50, ema_200, _macd, _rsi = await asyncio.gather(ema(exchange, symbol, 50, timeframe),
                                                        ema(exchange, symbol, 200, timeframe),
                                                        macd(exchange, symbol, timeframe),
                                                        rsi(exchange, symbol, timeframe))
    
    if not ema_50 or not ema_200 or not _macd or not _rsi:
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return
    
    trend = ""
    sig_type = None

    # check EMA values
    if ema_50[0]['EMA_50'] > ema_200[0]['EMA_200']:
        # if ema_50[1]['EMA_50'] <= ema_200[1]['EMA_200']:
        #     sig_type = 'EMA_BUY'
        trend = "UPTREND"
    elif ema_50[0]['EMA_50'] < ema_200[0]['EMA_200']:
        # if ema_50[1]['EMA_50'] >= ema_200[1]['EMA_200']:
        #     sig_type = 'EMA_SELL'
        trend = "DOWNTREND"

    # Confirm with MACD value
    signal = watchlist.get(symbol)
    if "RSI" not in signal:
        if _macd[0]['MACDh_12_26_9'] > 0:
            if _macd[1]['MACDh_12_26_9'] <= 0:  # macd just inverted upward
                if trend == 'UPTREND':
                    sig_type = 'MACD_EMA_BUY'
                elif trend == 'DOWNTREND':
                    sig_type = 'NEUTRAL'
        if _macd[0]['MACDh_12_26_9'] < 0:
            if _macd[1]['MACDh_12_26_9'] >= 0:  # macd just inverted downwards
                if trend == 'UPTREND':
                    sig_type = 'NEUTRAL'
                elif trend == 'DOWNTREND':
                    sig_type = 'MACD_EMA_SELL'
                
    # confirm with rsi
    if "RSI" in signal:
        if trend == 'UPTREND':
            if _rsi[0]['RSI_6'] < _rsi[1]['RSI_6']:
                watchlist.reset(symbol)
        elif trend == 'DOWNTREND':
            if _rsi[0]['RSI_6'] > _rsi[1]['RSI_6']:
                watchlist.reset(symbol)
            
    if trend == 'UPTREND':
        if _rsi[0]['RSI_6'] > 70:
            sig_type = 'NEUTRAL'
        elif _rsi[0]['RSI_6'] <= 30 or _rsi[1]['RSI_6'] <= 30:
            if _rsi[1]['RSI_6'] > _rsi[0]['RSI_6']:
                sig_type = "RSI_EMA_BUY"

    if trend == 'DOWNTREND':
        if _rsi[0]['RSI_6'] < 30:
            sig_type = 'NEUTRAL'
        elif _rsi[0]['RSI_6'] >= 70 or _rsi[1]['RSI_6'] >= 70:
            if _rsi[1]['RSI_6'] > _rsi[0]['RSI_6']:
                sig_type = "RSI_EMA_SELL"

    if sig_type is not None:
        watchlist.put(symbol, sig_type)
        if sig_type != 'NEUTRAL':
            await run_thread(symbol, sig_type)
        

async def main():
    print("Loading markets...")
    exchange.load_markets()
    symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'WAVES/USDT', 'ETC/USDT', 'XRP/USDT']
    tasks = [analyser(symbol, exchange) for symbol in symbols]
    await asyncio.gather(*tasks)
    all_sym = watchlist.get_all()
    adapter.info(all_sym)
    
if __name__ == '__main__':
    asyncio.run(main())
