#!/usr/bin/python3

from ta.analyser import analyser
from datetime import datetime
from helper.adapter import adapter
from exchange import bybit as exchange

import asyncio


async def main():
    symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'WAVES/USDT', 'ETC/USDT',
               'DOGE/USDT', 'BNB/USDT', 'DOT/USDT']
    # mkt = exchange.load_markets()
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
            if current_dt.minute >= 55:
                hour = current_dt.hour + 1
                minute = 0
            elif current_dt.minute % 5 > 0:
                minute = current_dt.minute + (5 - (current_dt.minute % 5))
                hour = current_dt.hour
            else:
                minute = current_dt.minute + 5
                hour = current_dt.hour

            next_time = datetime(current_dt.year, current_dt.month,
                                current_dt.day, hour, minute, 0)
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
