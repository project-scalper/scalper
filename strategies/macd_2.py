#!/usr/bin/python3

from utils.ema_calculator import ema
from utils.macd_calculator import macd
from utils.rsi_calculator import rsi
import threading
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe
import asyncio
import ccxt

active = False


def start_checker(symbol, signal, exchange):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(new_checker(symbol, signal, exchange))

async def run_thread(symbol, sig_type, exchange):
    nt = threading.Thread(target=start_checker, args=(symbol, sig_type, exchange))
    nt.start()

async def new_checker(symbol, sig_type, exchange):
    from strategies.checker import Checker
    trade = Checker(exchange)
    await trade.execute(symbol, signal=sig_type)


async def analyser(symbol:str, exchange:ccxt.Exchange)-> None:
    for n in range(3):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=210)
            break
        except Exception as e:
            if n == 2:
                adapter.warning(f"Unable to fetch ohlcv for {symbol}")
                return None
    ema_50, ema_100, _macd, _rsi = await asyncio.gather(ema(exchange, symbol, 50, timeframe, ohlcv=ohlcv),
                                                        ema(exchange, symbol, 100, timeframe, ohlcv=ohlcv),
                                                        macd(exchange, symbol, timeframe, ohlcv=ohlcv),
                                                        rsi(exchange, symbol, timeframe, ohlcv=ohlcv))
    
    if not ema_50 or not ema_100 or not _macd or not _rsi:
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return
    
    trend = 'NEUTRAL'
    sig_type = None

    # check EMA values
    if (ema_50[0]['EMA'] > ema_100[0]['EMA']) and (ohlcv[-1][-2] > ema_50[0]['EMA']):
        # if ohlcv[-1][-2] > ema_50[0]['EMA']:
        trend = "UPTREND"
    elif (ema_50[0]['EMA'] < ema_100[0]['EMA']) and (ohlcv[-1][-2] < ema_50[0]['EMA']):
        # if ohlcv[-1][-2] < ema_50[0]['EMA']:
        trend = "DOWNTREND"

    # Confirm with MACD value
    signal = watchlist.get(symbol)
    if "RSI" not in signal and 'MACD' not in signal:
        if trend == 'UPTREND' and _macd[0]['MACD'] < 0:
            if _macd[1]['MACD'] < _macd[0]['MACD']:     # macd is -ve and starts increasing
                if (_macd[2]['MACD'] < _macd[1]['MACD']) and (_macd[3]['MACD'] > _macd[2]['MACD']):
                    sig_type = 'MACD_EMA_2_BUY'
            else:
                sig_type = 'NEUTRAL'
        elif trend == 'DOWNTREND' and _macd[0]['MACD'] > 0:
            if _macd[1]['MACD'] > _macd[0]['MACD']:     # macd is +ve and starts decreasing
                if (_macd[2]['MACD'] > _macd[1]['MACD']) and (_macd[3]['MACD'] < _macd[2]['MACD']):
                    sig_type = 'MACD_EMA_2_SELL'
            else:
                sig_type = 'NEUTRAL'

        # if _macd[0]['MACDh_12_26_9'] > 0:
        #     if _macd[1]['MACDh_12_26_9'] <= 0:  # macd just inverted upward
        #         if trend == 'UPTREND':
        #             sig_type = 'MACD_EMA_BUY'
        #         elif trend == 'DOWNTREND':
        #             sig_type = 'NEUTRAL'
        # if _macd[0]['MACDh_12_26_9'] < 0:
        #     if _macd[1]['MACDh_12_26_9'] >= 0:  # macd just inverted downwards
        #         if trend == 'UPTREND':
        #             sig_type = 'NEUTRAL'
        #         elif trend == 'DOWNTREND':
        #             sig_type = 'MACD_EMA_SELL'
                
    # confirm with rsi
    if "RSI" in signal:
        if trend == 'UPTREND':
            if _rsi[0]['RSI_6'] < _rsi[1]['RSI_6']:
                watchlist.reset(symbol)
        elif trend == 'DOWNTREND':
            if _rsi[0]['RSI_6'] > _rsi[1]['RSI_6']:
                watchlist.reset(symbol)
            
    if sig_type is None:
        if trend == 'UPTREND':
            if _rsi[0]['RSI_6'] > 85:
                sig_type = 'NEUTRAL'
            elif (_rsi[0]['RSI_6'] < 15 or _rsi[1]['RSI_6'] < 15) and _rsi[1]['RSI_6'] < _rsi[0]['RSI_6']:
                sig_type = "RSI_EMA_BUY"

        elif trend == 'DOWNTREND':
            if _rsi[0]['RSI_6'] < 15:
                sig_type = 'NEUTRAL'
            elif (_rsi[0]['RSI_6'] >= 85 or _rsi[1]['RSI_6'] >= 85) and _rsi[1]['RSI_6'] > _rsi[0]['RSI_6']:
                sig_type = "RSI_EMA_SELL"

    if sig_type is not None:
        watchlist.put(symbol, sig_type)
        if sig_type != 'NEUTRAL':
            await run_thread(symbol, sig_type, exchange)
        
