#!/usr/bin/python3

# from utils.t3_calculator import t3
# from utils.adx_calculator import adx
from utils.ema_calculator import ema
from utils.bbands_calculator import bbands
from utils.rsi_calculator import rsi
from utils.mavol_calculator import mavol
from executor.checker import Checker
import threading
from typing import Dict, Union, List
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe, exchange
from model import storage
# from datetime import datetime, timedelta
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

    _ema_9, _ema_21, _bbands, _rsi, _mavol  = await asyncio.gather(
                                        ema(exchange, symbol, 9, timeframe, ohlcv=ohlcv),
                                        ema(exchange, symbol, 21, timeframe, ohlcv=ohlcv),
                                        bbands(exchange, symbol, ohlcv=ohlcv),
                                        rsi(exchange, symbol, timeframe, ohlcv=ohlcv),
                                        mavol(exchange, symbol, 20, ohlcv=ohlcv))
    
    if not _ema_9 or not _ema_21 or not _bbands or not _rsi:
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return

    # check EMA9 and EMA21 to determine trend
    if _ema_9[0]['EMA'] > _ema_21[0]['EMA']:
        trend = 'UPTREND'
    elif _ema_9[0]['EMA'] < _ema_21[0]['EMA']:
        trend = 'DOWNTREND'
    else:
        trend = "NEUTRAL"


    # Check if price just cross any of the EMA lines or if the EMAs just crossed themselves
    sig = None
    if trend == 'UPTREND':
        if (min(ohlcv[-1][4], ohlcv[-1][1]) > _ema_9[0]['EMA']) and (min(ohlcv[-2][4], ohlcv[-2][1]) < _ema_9[1]['EMA']):
            sig = 'BREAKOUT_BUY'
        if _ema_9[1]['EMA'] < _ema_21[1]['EMA']:
            sig = 'CROSS_BUY'
    if trend == 'DOWNTREND':
        if (max(ohlcv[-1][4], ohlcv[-1][1]) < _ema_9[0]['EMA']) and (max(ohlcv[-2][4], ohlcv[-2][1]) > _ema_9[1]['EMA']):
            sig = 'BREAKOUT_SELL'
        if _ema_9[1]['EMA'] > _ema_21[1]['EMA']:
            sig = 'CROSS_SELL'

    # Return None if no signal indicates
    if not sig:
        return None
    
    # Confirm with rsi value
    if _rsi[0]['RSI'] >= 30 and _rsi[0]['RSI'] <= 70:
        rsi_check = True
    else:
        rsi_check = False

    # Confirm price with bollinger bands
    bbands_check = False
    if trend == 'UPTREND':
        if ohlcv[-1][4] > _bbands[0]['MIDDLE']:
            bbands_check = True
    elif trend == 'DOWNTREND':
        if ohlcv[-1][4] < _bbands[0]['MIDDLE']:
            bbands_check = True

    # confirm with moving average volume indicator
    if ohlcv[-1][5] >= _mavol[0]['MAVOL']:
        mavol_check = True

    # Check if the indicators has reversed for existing signal
    signal = watchlist.get(symbol)
    if "BUY" in signal:
        if _ema_9[0]['EMA'] < _ema_21[0]['EMA']:
            watchlist.reset(symbol)
    elif "SELL" in signal:
        if _ema_9[0]['EMA'] > _ema_21[0]['EMA']:
            watchlist.reset(symbol)

    if "BUY" in sig or "SELL" in sig:
        if (trend == 'UPTREND'):
            stop_loss = _bbands[0]['LOWER']
        else:
            stop_loss = _bbands[0]['UPPER']

        if rsi_check and bbands_check and mavol_check:
            return {'symbol': symbol, 'signal': sig, 'stop_loss': stop_loss}
    return None
        

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
