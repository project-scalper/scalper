#!/usr/bin/python3

# from strategies.macd import analyser
# from strategies.rsi_strategy import analyser
from strategies.macd_2 import analyser
from datetime import datetime, timedelta
from helper.adapter import adapter
from exchange import bybit as exchange
from datetime import datetime, timedelta

import asyncio


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
            await asyncio.gather(*tasks)
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
