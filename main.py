#!/usr/bin/python3

# from strategies.macd import analyser
# from strategies.rsi_strategy import analyser
# from strategies.macd_2 import analyser
# from strategies.psar_ema import analyser
from strategies.adx_psar import analyser
from datetime import datetime, timedelta
from helper.adapter import adapter
from variables import exchange
from datetime import datetime, timedelta
from model import storage
import threading
# import ccxt
from executor.checker import Checker
from itertools import cycle

import asyncio


async def run_thread(symbol, sig_type, bot_id):
    nt = threading.Thread(target=set_event, args=(symbol, sig_type, bot_id))
    nt.start()

def set_event(symbol, signal, bot_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(new_checker(symbol, signal, bot_id))

async def new_checker(symbol, sig_type, bot_id):
    trade = Checker(exchange, bot_id=bot_id)
    await trade.execute(symbol, sig_type, reverse=False)


async def main():
    symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'ADA/USDT:USDT', 'SOL/USDT:USDT',
               'DOGE/USDT:USDT', 'BNB/USDT:USDT', 'DOT/USDT:USDT', 'XRP/USDT:USDT',
               'MATIC/USDT:USDT', 'SAND/USDT:USDT', 'GALA/USDT:USDT', 'AVAX/USDT:USDT',
               'APE/USDT:USDT', 'LINK/USDT:USDT', 'NEAR/USDT:USDT']
    # run_to = datetime.now() + timedelta(hours=24)
    mkt = exchange.load_markets()
    while True:
        try:
            tasks = [analyser(symbol, exchange) for symbol in symbols]
            adapter.info("Starting analysis...")
            signals = await asyncio.gather(*tasks)
            signals = list(filter(lambda x: x is not None, signals))
            cycled_signal = cycle(signals)
            if len(signals) > 0:
                bots = storage.search("Bot", active=True, available=True)
                # result = {}
                for bot in bots:
                    await run_thread(sig['symbol'], sig['signal'], bot_id=bot.id)
                # for i, bot in enumerate(list(bots.values())):
                    # sig = signals[i % len(signals)]
                    # if bot.available is False:
                        # continue
                    # await run_thread(sig['symbol'], sig['signal'], bot_id=bot.id)
                    # result[item] = signals[i % len(signals)]
            adapter.info("Analysis completed.")
        except Exception as e:
            msg = f"{type(e).__name__} - {str(e)}"
            adapter.error(msg)
        finally:
            current_dt = datetime.now()
            next_time = current_dt + timedelta(minutes=5)
            if next_time.minute % 5 != 0:
                minute = next_time.minute - (next_time.minute % 5)
                next_time = next_time.replace(minute=minute)

            next_time = next_time.replace(second=0, microsecond=0)
            while datetime.now() < next_time:
                pass


if __name__ == '__main__':
    current_dt = datetime.now()
    if current_dt.minute >= 55:
        hour = current_dt.hour + 1
        minute = 0
    elif current_dt.minute % 5 > 0:
        minute = current_dt.minute + (5 - (current_dt.minute % 5))
        hour = current_dt.hour

    start_time = datetime(current_dt.year, current_dt.month,
                        current_dt.day, hour, minute, 0)
    if datetime.now() >= start_time:
        asyncio.run(main())
