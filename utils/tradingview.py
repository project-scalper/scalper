#!/usr/bin/python3

from tradingview_ta import Interval, TA_Handler
from datetime import datetime, timedelta
# from variables import timeframe


def get_analysis(symbol):
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
    return analysis


def main():
    symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'ADA/USDT:USDT', 'SOL/USDT:USDT',
               'DOGE/USDT:USDT', 'BNB/USDT:USDT', 'DOT/USDT:USDT', 'XRP/USDT:USDT',
               'MATIC/USDT:USDT', 'SAND/USDT:USDT', 'GALA/USDT:USDT', 'AVAX/USDT:USDT',
               'APE/USDT:USDT', 'LINK/USDT:USDT', 'NEAR/USDT:USDT']
    prev_sig = {}
    while True:
        print("Starting")
        try:
            for symbol in symbols:
                analysis = get_analysis(symbol)['RECOMMENDATION']
                if "BUY" in analysis:
                    if prev_sig.get(symbol, None) == 'sell':
                        print(f'#{symbol} {analysis}')
                    prev_sig[symbol] = 'buy'
                elif 'SELL' in analysis:
                    if prev_sig.get(symbol, None) == 'buy':
                        print(f"#{symbol} {analysis}")
                    prev_sig[symbol] = 'sell'
            print("Done!")
        except Exception as e:
            print(e)
        finally:
            next_time = datetime.now() + timedelta(minutes=5)
            if next_time.minute % 5 != 0:
                minute = next_time.minute - (next_time.minute % 5)
                next_time = next_time.replace(minute=minute)

            next_time = next_time.replace(second=0, microsecond=0)
            while datetime.now() < next_time:
                pass



if __name__ == '__main__':
    # symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'ADA/USDT:USDT', 'SOL/USDT:USDT',
    #            'DOGE/USDT:USDT', 'BNB/USDT:USDT', 'DOT/USDT:USDT', 'XRP/USDT:USDT',
    #            'MATIC/USDT:USDT', 'SAND/USDT:USDT', 'GALA/USDT:USDT', 'AVAX/USDT:USDT',
    #            'APE/USDT:USDT', 'LINK/USDT:USDT', 'NEAR/USDT:USDT']
    # for symbol in symbols:
    #     try:
    #         analysis = get_analysis(symbol)
    #         print(f"#{symbol} - {analysis}")
    #     except Exception as e:
    #         print(f"\n#{symbol} - {str(e)}\n")

    main()