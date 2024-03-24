#!/usr/bin/python3

from utils.ema_calculator import ema
from utils.macd_calculator import macd
from utils.rsi_calculator import rsi
from utils.candle_patterns import candle_main
import threading
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe
import asyncio
import ccxt
from model import storage
from utils.tradingview import get_analysis

active = False


def start_checker(symbol, signal, exchange):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(new_checker(symbol, signal, exchange))

async def run_thread(symbol, sig_type, exchange):
    nt = threading.Thread(target=start_checker, args=(symbol, sig_type, exchange))
    nt.start()

async def new_checker(symbol, sig_type:str, exchange):
    from executor.checker import Checker
    
    bots = storage.all("Bot")
    for _, bot in bots.items():
        # if bot.balance < bot.capital * 0.9:
        #     adapter.error("Insufficient capital")
        cap = int(bot.capital)
        
        trade = Checker(exchange, bot_id=bot.id, capital=cap)

        # count = 0
        # for pnl in bot.pnl_history:
        #     if pnl < 0:
        #         count += 1
        # if count >= 5:
        #     if "BUY" in sig_type:
        #         sig_type = sig_type.replace("BUY", "SELL")
        #     elif "SELL" in sig_type:
        #         sig_type = sig_type.replace("SELL", "BUY")
        #     watchlist.put(symbol, sig_type)
            
        await trade.execute(symbol, signal=sig_type, reverse=False)


async def analyser(symbol:str, exchange:ccxt.Exchange)-> None:
    for n in range(3):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=210)
            break
        except Exception as e:
            if n == 2:
                adapter.warning(f"Unable to fetch ohlcv for {symbol} - {str(e)}")
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

    # check EMA values to get trend
    if (ema_50[0]['EMA'] > ema_100[0]['EMA']):
    # if (ema_50[0]['EMA'] > ema_100[0]['EMA']) and (ohlcv[-1][-2] > ema_50[0]['EMA']):
        trend = "UPTREND"
    elif (ema_50[0]['EMA'] < ema_100[0]['EMA']):
    # elif (ema_50[0]['EMA'] < ema_100[0]['EMA']) and (ohlcv[-1][-2] < ema_50[0]['EMA']):
        trend = "DOWNTREND"

    # Confirm with MACD value
    signal = watchlist.get(symbol)
    # if "RSI" not in signal and 'MACD' not in signal:
        # if trend == 'UPTREND' and _macd[0]['MACD'] < 0:
    if trend == 'UPTREND':
        if (_macd[1]['MACD'] < _macd[0]['MACD']) and (_macd[2]['MACD'] > _macd[1]['MACD']):     # macd starts increasing
        #     if (_macd[2]['MACD'] < _macd[1]['MACD']) and (_macd[3]['MACD'] > _macd[2]['MACD']):
            sig_type = 'MACD_EMA_2_BUY'
        else:
            sig_type = 'NEUTRAL'

        # elif trend == 'DOWNTREND' and _macd[0]['MACD'] > 0:
    elif trend == 'DOWNTREND':
        if (_macd[1]['MACD'] > _macd[0]['MACD']) and (_macd[2]['MACD'] < _macd[1]['MACD']):     # macd starts decreasing
            # if (_macd[2]['MACD'] > _macd[1]['MACD']) and (_macd[3]['MACD'] < _macd[2]['MACD']):
                sig_type = 'MACD_EMA_2_SELL'
        else:
            sig_type = 'NEUTRAL'

    # Return signal type to NEUTRAL if macd changes
    if "MACD" in signal and "BUY" in signal:
        if _macd[1]['MACD'] > _macd[0]['MACD']:
            sig_type = 'NEUTRAL'
    elif "MACD"in signal and "SELL" in signal:
        if _macd[1]['MACD'] < _macd[0]['MACD']:
            sig_type = 'NEUTRAL'
                
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
            if _rsi[0]['RSI_6'] > 80:
                sig_type = 'NEUTRAL'
            elif (_rsi[0]['RSI_6'] < 20 or _rsi[1]['RSI_6'] < 20) and _rsi[1]['RSI_6'] < _rsi[0]['RSI_6']:
                sig_type = "RSI_EMA_BUY"

        elif trend == 'DOWNTREND':
            if _rsi[0]['RSI_6'] < 20:
                sig_type = 'NEUTRAL'
            elif (_rsi[0]['RSI_6'] >= 80 or _rsi[1]['RSI_6'] >= 80) and _rsi[1]['RSI_6'] > _rsi[0]['RSI_6']:
                sig_type = "RSI_EMA_SELL"


    if sig_type is not None:
        signal = watchlist.get(symbol)
        # confirm_ema_50, confirm_ema_100 = await asyncio.gather(ema(exchange, symbol, 50, confirmation_timeframe),
        #                                                  ema(exchange, symbol, 100, confirmation_timeframe))
        if "BUY" in sig_type or "BUY" in signal:
            # check higher tf to confirm trend
            # if confirm_ema_100[0]['EMA'] > confirm_ema_50[0]['EMA']:
            #     sig_type = 'NEUTRAL'

            if _rsi[0]['RSI_6'] > 80:
                sig_type = 'NEUTRAL'
            if ohlcv[-2][4] <= ohlcv[-2][1]:
                sig_type = 'NEUTRAL'

        elif "SELL" in sig_type or "SELL" in signal:
            # check higher tf to confirm trend
            # if confirm_ema_100[0]['EMA'] < confirm_ema_50[0]['EMA']:
            #     sig_type = 'NEUTRAL'

            if _rsi[0]['RSI_6'] < 20:
                sig_type = 'NEUTRAL'
            if ohlcv[-2][4] >= ohlcv[-2][1]:
                sig_type = 'NEUTRAL'
                
        watchlist.put(symbol, sig_type)

        # candle_analysis = candle_main(ohlcv=ohlcv, signal=sig_type)
        tv_analysis = get_analysis(symbol)
        if ("BUY" in sig_type and "BUY" in tv_analysis) or ("SELL" in sig_type and 'SELL' in tv_analysis):
            if sig_type != "NEUTRAL":
                await run_thread(symbol, sig_type, exchange)
                # watchlist.reset(symbol)
                return
        
