#!/usr/bin/python3

from utils.adx_calculator import adx
from utils.atr_calculator import atr
from utils.bbands_calculator import bbands
from utils.rsi_calculator import rsi
from utils.macd_calculator import macd
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
    """
    A strategy that uses Bollinger bands, MACD and Average True Range(ATR)
    Args:
        symbol: The string code for the ticker
        exchange: A ccxt exhange object
        ohlcv: A list of symbol history data
    Return:
        A dict of trade details or None when no trade is found
    """

    # Fetch ohlcv data
    if len(ohlcv) == 0:
        for n in range(3):
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=210)
                break
            except Exception as e:
                if n == 2:
                    adapter.warning(f"Unable to fetch ohlcv for {symbol} - {str(e)}")
                    return None

    # Fetch all the required indicators
    _adx, _atr, _rsi, _bbands, _macd = await asyncio.gather(adx(exchange, symbol, timeframe, ohlcv=ohlcv),
                                       atr(exchange, symbol, timeframe, ohlcv=ohlcv),
                                       rsi(exchange, symbol, timeframe, ohlcv=ohlcv),
                                       bbands(exchange, symbol, ohlcv=ohlcv),
                                       macd(exchange, symbol, timeframe, ohlcv=ohlcv))
    
    if not all([_adx, _atr, _rsi, _bbands]):
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return None

    trend = 'NEUTRAL'


    # check if intial signal has reversed
    initial_sig = watchlist.get(symbol)
    if "BUY" in initial_sig:
        if _macd[0]['MACD'] < 0:
            watchlist.reset(symbol)
        else:
            return None

    elif "SELL" in initial_sig:
        if _macd[0]['MACD'] > 0:
            watchlist.reset(symbol)
        else:
            return None


    # check for breakouts from bband
    if (ohlcv[-1][4] > _bbands[0]["UPPER"]):
        trend = "UPTREND"
    elif (ohlcv[-1][4]) < _bbands[0]["LOWER"]:
        trend = "DOWNTREND"


    # confirm with rsi and adx then return successful trades
    if trend == "UPTREND" and _macd[0]['MACD'] > 0:
        if 30 < _rsi[0]['RSI'] < 70:
            sig_type = "BOLL_MACD_BUY"
            watchlist.put(symbol, sig_type)
            return {"symbol": symbol, "signal": sig_type, 
                "atr": _atr[0]["ATR"], "entry_price": ohlcv[-1][4]}
    elif (trend == "DOWNTREND" and _macd[0]["MACD"] < 0):
        if 30 < _rsi[0]['RSI'] < 70:
            sig_type = "BOLL_MACD_SELL"
            watchlist.put(symbol, sig_type)
            return {"symbol": symbol, "signal": sig_type, 
                "atr": _atr[0]["ATR"], "entry_price": ohlcv[-1][4]}
        
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
