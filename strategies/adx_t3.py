#!/usr/bin/python3

from utils.t3_calculator import t3
from utils.adx_calculator import adx
from utils.ema_calculator import ema
from executor.checker import Checker
import threading
from typing import Dict, Union, List
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe, exchange
from model import storage
from datetime import datetime, timedelta
import asyncio
import ccxt


def start_checker(symbol, signal, _psar):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(new_checker(symbol, signal, _psar))

async def run_thread(symbol, sig_type, _psar):
    nt = threading.Thread(target=start_checker, args=(symbol, sig_type, _psar))
    nt.start()

async def new_checker(symbol, sig_type, _psar):
    bots = storage.all("Bot")
    for _, bot in bots.items():
        cap = int(bot.capital)
        # if bot.balance < cap * 0.9:
        #     adapter.warning(f"Insufficient balance for bot: {bot.id}")
        #     continue
        exchange:ccxt.Exchange = bot.get_exchange()

        trade = Checker(exchange, capital=cap, bot_id=bot.id, psar=_psar)
        await trade.execute(symbol, sig_type, reverse=False)


async def analyser(symbol:str, exchange:ccxt.Exchange, ohlcv:List=[])-> Union[Dict | None]:
    if len(ohlcv) == 0:
        for n in range(3):
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=210)
                break
            except Exception as e:
                if n == 2:
                    adapter.warning(f"Unable to fetch ohlcv for {symbol} - {str(e)}")
                    return None

    _adx, _t3, _ema_50, _ema_100 = await asyncio.gather(adx(exchange, symbol, timeframe, ohlcv=ohlcv),
                                       t3(exchange, symbol, timeframe, ohlcv=ohlcv),
                                       ema(exchange, symbol, 50, timeframe, ohlcv=ohlcv),
                                       ema(exchange, symbol, 100, timeframe, ohlcv=ohlcv))
    
    if not _adx or not _t3:
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return

    trend = 'NEUTRAL'

    # check DMI and ADX to determine trend
    if (_adx[0]['DMP'] > _adx[0]['DMN']) and (_adx[0]['ADX'] >= 25):
        if _ema_50[0]['EMA'] > _ema_100[0]['EMA']:
            trend = 'UPTREND'
    elif (_adx[0]['DMP'] < _adx[0]['DMN']) and (_adx[0]['ADX'] >= 25):
        if _ema_50[0]['EMA'] < _ema_100[0]['EMA']:
            trend = 'DOWNTREND'
    else:
        trend = "NEUTRAL"

    # last_dt_on_ohlcv = datetime.fromtimestamp(ohlcv[-1][0] / 1000)
    # if datetime.now() - timedelta(minutes=5) > last_dt_on_ohlcv:
    #     ohlcv.append([])

    # Confirm with T3 value
    sig_type = ""
    if trend == 'UPTREND':
        if (_t3[0]['FAST_T3'] > _t3[0]['SLOW_T3']) and (_t3[1]['FAST_T3'] <= _t3[1]['SLOW_T3']):
            if ohlcv[-1][4] > _t3[0]['SLOW_T3']:
                sig_type = "ADX_T3_CROSS_BUY"
                stop_loss = min(_t3[0]['FAST_T3'], _t3[0]['SLOW_T3'])
                watchlist.put(symbol, sig_type)
        # elif (_t3[0]['FAST_T3'] > _t3[0]['SLOW_T3']) and (_t3[1]['FAST_T3'] > ohlcv[-2][4]) and (ohlcv[-1][4] > _t3[0]['FAST_T3']):
        elif (max(_t3[1]['SLOW_T3'], _t3[1]['FAST_T3']) > min(ohlcv[-2][4], ohlcv[-2][1])): # breakout candle
            if (min(ohlcv[-1][1], ohlcv[-1][4]) > max(_t3[0]['FAST_T3'], _t3[0]['SLOW_T3'])):   # confirmation candle
                sig_type = "ADX_T3_BREAKOUT_BUY"
                stop_loss = min(_t3[0]['FAST_T3'], _t3[0]['SLOW_T3'])
                watchlist.put(symbol, sig_type)

    elif trend == 'DOWNTREND':
        if (_t3[0]['SLOW_T3'] > _t3[0]['FAST_T3']) and (_t3[1]['SLOW_T3'] <= _t3[1]['FAST_T3']):
            if ohlcv[-1][4] > _t3[0]['FAST_T3']:
                sig_type = "ADX_T3_CROSS_SELL"
                stop_loss = max(_t3[0]['FAST_T3'], _t3[0]['SLOW_T3'])
                watchlist.put(symbol, sig_type)
        # elif (_t3[0]['SLOW_T3'] > _t3[0]['FAST_T3']) and (ohlcv[-2][4] > _t3[1]['FAST_T3']) and (_t3[0]['FAST_T3'] > ohlcv[-1][4]):
        elif (max(ohlcv[-2][1], ohlcv[-2][4]) > min(_t3[1]['FAST_T3'], _t3[1]['SLOW_T3'])):
            if (min(_t3[0]['FAST_T3'], _t3[0]['SLOW_T3']) > max(ohlcv[-1][1], ohlcv[-1][4])):
                sig_type = "ADX_T3_BREAKOUT_SELL"
                stop_loss = max(_t3[0]['FAST_T3'], _t3[0]['SLOW_T3'])
                watchlist.put(symbol, sig_type)

    if "BUY" in sig_type or "SELL" in sig_type:
        sig_type = sig_type +  "_" + str(round(_adx[0]['ADX'], 2))
        watchlist.put(symbol, sig_type)

    # Check if the indicators has reversed for existing signal
    signal = watchlist.get(symbol)
    if "BUY" in signal:
        # if _adx[0]['DMN'] > _adx[0]['DMP']:
        #     watchlist.reset(symbol)
        # if _t3[0]['FAST_T3'] > ohlcv[-1][4]:
        #     watchlist.reset(symbol)
        if _ema_50[0]['EMA'] < _ema_100[0]['EMA']:
            watchlist.reset(symbol)
    elif "SELL" in signal:
        # if _adx[0]['DMP'] > _adx[0]['DMN']:
        #     watchlist.reset(symbol)
        # if ohlcv[-1][4] > _t3[0]['FAST_T3']:
        #     watchlist.reset(symbol)
        if _ema_50[0]['EMA'] > _ema_100[0]['EMA']:
            watchlist.reset(symbol)

    if "BUY" in sig_type or "SELL" in sig_type:
        return {'symbol': symbol, 'signal': sig_type, 'stop_loss': stop_loss}
    return None
        # await run_thread(symbol, sig_type, _psar=_psar[0]['PSAR'])
        

async def main():
    print("Loading markets...")
    exchange.load_markets()
    symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'ADA/USDT:USDT', 'SOL/USDT', 'WAVES/USDT', 'ETC/USDT']
    tasks = [analyser(symbol, exchange) for symbol in symbols]
    await asyncio.gather(*tasks)
    all_sym = watchlist.get_all()
    adapter.info(all_sym)
    
if __name__ == '__main__':
    asyncio.run(main())
