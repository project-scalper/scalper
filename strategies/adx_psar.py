#!/usr/bin/python3

from utils.ema_calculator import ema
from utils.rsi_calculator import rsi
from utils.adx_calculator import adx
from utils.tradingview import get_analysis
from utils.psar_calculator import psar
from executor.checker import Checker
from utils.candle_patterns import candle_main
import threading
from typing import Dict, Union
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


async def analyser(symbol:str, exchange:ccxt.Exchange)-> Union[Dict | None]:
    for n in range(3):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=210)
            break
        except Exception as e:
            if n == 2:
                adapter.warning(f"Unable to fetch ohlcv for {symbol} - {str(e)}")
                return None

    _adx, _psar = await asyncio.gather(adx(exchange, symbol, timeframe, ohlcv=ohlcv),
                                       psar(exchange, symbol, timeframe, ohlcv=ohlcv))
    
    if not _adx or not _psar:
        adapter.warning(f"One or more indicators are missing for {symbol}")
        return
    
    watchlist.psar_put(symbol, _psar[0]['PSAR'])

    # check ADX to determine trend
    if _adx[0]['DMP'] > _adx[0]['DMN']:
        trend = 'UPTREND'
    elif _adx[0]['DMP'] < _adx[0]['DMN']:
        trend = 'DOWNTREND'
    else:
        trend = "NEUTRAL"

    last_dt_on_ohlcv = datetime.fromtimestamp(ohlcv[-1][0] / 1000)
    if datetime.now() - timedelta(minutes=5) > last_dt_on_ohlcv:
        ohlcv.append([])

    # Confirm with PSAR value
    sig_type = ""
    if trend == 'UPTREND':
        if (_psar[0]['PSAR'] < ohlcv[-2][-2]) and (_psar[1]['PSAR'] < ohlcv[-3][-2]):
            if (_psar[2]['PSAR'] < ohlcv[-4][-2]) and (_psar[3]['PSAR'] > ohlcv[-5][-2]):
                if _adx[0]['ADX'] >= 25:
                    sig_type = 'PSAR_ADX_BUY'
                else:
                    sig_type = 'PSAR_BUY'
                watchlist.put(symbol, sig_type)

    elif trend == 'DOWNTREND':
        if (_psar[0]['PSAR'] > ohlcv[-2][-2]) and (_psar[1]['PSAR'] > ohlcv[-3][-2]):
            if (_psar[2]['PSAR'] > ohlcv[-4][-2]) and (_psar[3]['PSAR'] < ohlcv[-5][-2]):
                if _adx[0]['ADX'] >= 25:
                    sig_type = 'PSAR_ADX_SELL'
                else:
                    sig_type = 'PSAR_SELL'
                watchlist.put(symbol, sig_type)

    # Check if the indicators has reversed for existing signal
    signal = watchlist.get(symbol)
    if "BUY" in signal:
        if trend != 'UPTREND':
            watchlist.reset(symbol)
        if _psar[0]['PSAR'] > ohlcv[-2][-2]:
            watchlist.reset(symbol)
    elif "SELL" in signal:
        if trend != 'DOWNTREND':
            watchlist.reset(symbol)
        if _psar[0]['PSAR'] < ohlcv[-2][-2]:
            watchlist.reset(symbol)

    if "BUY" in sig_type or "SELL" in sig_type:
        return {'symbol': symbol, 'signal': sig_type}
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
