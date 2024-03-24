#!/usr/bin/python3

from tradingview_ta import Interval, TA_Handler
from datetime import datetime, timedelta
from helper.adapter import adapter
from typing import Literal
# from variables import timeframe


def get_analysis(symbol) -> Literal["BUY", "SELL", "STRONG_BUY", "STRONG_SELL"]:
    symbol = symbol.split("/")[0]
    symbol += "USDT"

    handler = TA_Handler(
        symbol=symbol,
        exchange='bybit',
        screener="crypto",
        interval=Interval.INTERVAL_5_MINUTES,
        timeout=None
    )

    analysis = handler.get_analysis().oscillators
    return analysis['RECOMMENDATION']


def main():
    symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'ADA/USDT:USDT', 'SOL/USDT:USDT',
               'DOGE/USDT:USDT', 'BNB/USDT:USDT', 'DOT/USDT:USDT', 'XRP/USDT:USDT',
               'MATIC/USDT:USDT', 'SAND/USDT:USDT', 'GALA/USDT:USDT', 'AVAX/USDT:USDT',
               'APE/USDT:USDT', 'LINK/USDT:USDT', 'NEAR/USDT:USDT']
    prev_sig = {}
    while True:
        adapter.info("Starting")
        try:
            for symbol in symbols:
                analysis = get_analysis(symbol)['RECOMMENDATION']
                if "BUY" in analysis:
                    if prev_sig.get(symbol, None) == 'sell':
                        adapter.info(f'#{symbol} {analysis}')
                    prev_sig[symbol] = 'buy'
                elif 'SELL' in analysis:
                    if prev_sig.get(symbol, None) == 'buy':
                        adapter.info(f"#{symbol} {analysis}")
                    prev_sig[symbol] = 'sell'
            adapter.info("Done!\n")
        except Exception as e:
            adapter.warning(e)
        finally:
            next_time = datetime.now() + timedelta(minutes=5)
            if next_time.minute % 5 != 0:
                minute = next_time.minute - (next_time.minute % 5)
                next_time = next_time.replace(minute=minute)

            next_time = next_time.replace(second=0, microsecond=0)
            while datetime.now() < next_time:
                pass



if __name__ == '__main__':

    main()