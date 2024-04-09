#!/usr/bin/python3

from utils.ema_calculator import ema
from utils.macd_calculator import macd
from utils.rsi_calculator import rsi
from utils.tradingview import get_analysis
from utils.psar_calculator import psar
from executor.checker import Checker
from utils.candle_patterns import candle_main
import threading
# from typing import Dict, List
from typing import Literal
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe, exchange
from model import storage
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


async def analyser(symbol:str, exchange:ccxt.Exchange)-> None:
    for n in range(3):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=210)
            break
        except Exception as e:
            if n == 2:
                adapter.warning(f"Unable to fetch ohlcv for {symbol} - {str(e)}")
                return None
            
    ema_100, _psar, _rsi = await asyncio.gather(ema(exchange, symbol, 100, timeframe, ohlcv=ohlcv),
                                          psar(exchange, symbol, timeframe, ohlcv=ohlcv),
                                          rsi(exchange, symbol, timeframe, ohlcv=ohlcv))
    
    if not ema_100 or not _psar:
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return
    
    watchlist.psar_put(symbol, _psar[0]['PSAR'])

    # check EMA_100 to determine trend
    if ema_100[0]['EMA_100'] < min(ohlcv[-2][1], ohlcv[-2][4]):
        trend = 'UPTREND'
    elif ema_100[0]['EMA_100'] > max(ohlcv[-2][1], ohlcv[-2][4]):
        trend = 'DOWNTREND'
    else:
        trend = "NEUTRAL"

    # Confirm with PSAR value
    sig_type = ""
    if trend == 'UPTREND':
        if (_psar[0]['PSAR'] < ohlcv[-2][-2]) and (_psar[1]['PSAR'] < ohlcv[-3][-2]):
            if (_psar[2]['PSAR'] < ohlcv[-4][-2]) and (_psar[3]['PSAR'] > ohlcv[-5][-2]):
                sig_type = 'PSAR_EMA_BUY'
                watchlist.put(symbol, sig_type)

    elif trend == 'DOWNTREND':
        if (_psar[0]['PSAR'] > ohlcv[-2][-2]) and (_psar[1]['PSAR'] > ohlcv[-3][-2]):
            if (_psar[2]['PSAR'] > ohlcv[-4][-2]) and (_psar[3]['PSAR'] < ohlcv[-5][-2]):
                sig_type = 'PSAR_EMA_SELL'
                watchlist.put(symbol, sig_type)

    # Check if the indicators has reversed for existing signal
    signal = watchlist.get(symbol)
    if "BUY" in signal:
        # if trend != 'UPTREND':
        #     watchlist.reset(symbol)
        if _psar[0]['PSAR'] > ohlcv[-2][-2]:
            watchlist.reset(symbol)
    elif "SELL" in signal:
        # if trend != 'DOWNTREND':
        #     watchlist.reset(symbol)
        if _psar[0]['PSAR'] < ohlcv[-2][-2]:
            watchlist.reset(symbol)
    
    # confirm the signal with rsi value
    if "BUY" in sig_type:
        if _rsi[0]['RSI'] < 70:
            sig_type = "RSI_" + sig_type
    if "SELL" in sig_type:
        if _rsi[0]['RSI'] > 30:
            sig_type = "RSI_" + sig_type

    if "BUY" in sig_type or "SELL" in sig_type:
        await run_thread(symbol, sig_type, _psar=_psar[0]['PSAR'])
        

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
