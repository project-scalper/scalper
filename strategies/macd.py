#!/usr/bin/python3

from utils.ema_calculator import ema
from utils.macd_calculator import macd
from utils.rsi_calculator import rsi
from utils.tradingview import get_analysis
# from utils import get_indicators
# from exchange import bybit as exchange
from executor.checker import Checker
from utils.candle_patterns import candle_main
import threading
# from typing import Dict, List
from typing import Literal, List
from helper.adapter import adapter
from helper import watchlist
from variables import timeframe, exchange
from model import storage
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
    bots = storage.all("Bot")
    for _, bot in bots.items():
        cap = int(bot.capital)
        trade = Checker(exchange, capital=cap, bot_id=bot.id)
        await trade.execute(symbol, sig_type, reverse=True)


async def analyser(symbol:str, exchange:ccxt.Exchange, ohlcv:List=[])-> None:
    if len(ohlcv) == 0:
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

    # check EMA values to determine trend
    if ema_50[0]['EMA_50'] > ema_100[0]['EMA_100']:
        trend = 'UPTREND'
    elif ema_50[0]['EMA_50'] < ema_100[0]['EMA_100']:
        trend = 'DOWNTREND'

    # Confirm with MACD value
    sig_type = None
    # signal = watchlist.get(symbol)
    if trend == 'UPTREND':
        if _macd[0]['MACD'] > 0 and _macd[1]['MACD'] < 0:   # macd just flipped upwards
            sig_type = "MACD_EMA_BUY"
        elif _macd[0]['MACD'] < 0:
            sig_type = 'NEUTRAL'

    elif trend == 'DOWNTREND':
        if _macd[0]['MACD'] < 0 and _macd[1]['MACD'] > 0:   # macd just flipped downwards
            sig_type = 'MACD_EMA_SELL'
        elif _macd[0]['MACD'] > 0:
            sig_type = 'NEUTRAL'
    
    if sig_type is not None:
        watchlist.put(symbol, sig_type)

    # confirm with rsi
    signal = watchlist.get(symbol)
    if "BUY" in signal and _rsi[0]['RSI_6'] > 70:
        watchlist.reset(symbol)
    if "SELL" in signal and _rsi[0]['RSI_6'] < 30:
        watchlist.reset(symbol)

    if sig_type and sig_type != 'NEUTRAL' and watchlist.get(symbol) != "NEUTRAL":
        tv_analysis = get_analysis(symbol)
        if ("BUY" in tv_analysis and "BUY" in sig_type) or ("SELL" in tv_analysis and "SELL" in sig_type):
            candle_analysis = candle_main(ohlcv=ohlcv, signal=sig_type)
            if candle_analysis is True:
                sig_type = "CS_" + sig_type
            return {'signal': sig_type, 'symbol': symbol}
            # await run_thread(symbol, sig_type)
        

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
