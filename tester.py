#!/usr/bin/python3

import asyncio
from variables import timeframe, exchange
from datetime import datetime
from strategies.adx_t3 import analyser as adx_t3
from strategies.macd import analyser as macd
from strategies.macd_2 import analyser as macd2
from strategies.psar_ema import analyser as psar_ema
from strategies.adx_psar import analyser as adx_psar
from strategies.rsi_strategy import analyser as rsi_str
from strategies.ema_rsi_boll import analyser as ema_rsi
from executor.checker import Checker
from colorama import Fore, Style


strategies = {'adx_t3': adx_t3, 'macd': macd,
        'macd2': macd2, 'psar_ema': psar_ema,
        'adx_psar': adx_psar, 'rsi_str': rsi_str, 'ema_boll_rsi': ema_rsi}

def tester(symbol, _ohlcv, name):
    good_trades = 0
    bad_trades = 0
    available = True
    # print(len(_ohlcv))
    active_trade = None
    analyser = strategies[name]

    for n in range(200, len(_ohlcv)):
        try:
            temp = _ohlcv[:n]
            # while len(temp[-1]) < 4:
            #     temp.pop(-1)
            resp = asyncio.run(analyser(symbol, exchange, ohlcv=temp))

            if active_trade:
                if len(temp[-1]) <= 4:
                    temp.pop(-1)
                if 'BUY' in active_trade.signal:
                    if temp[-1][3] <= active_trade.sl:
                        bad_trades += 1
                        available = True
                        print(f"{Fore.RED}{start_dt}, entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")
                    elif temp[-1][2] >= active_trade.tp:
                        good_trades += 1
                        available = True
                        active_trade = None
                        print(f"{Fore.GREEN}{start_dt}, entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")

                elif 'SELL' in active_trade.signal:
                    if temp[-1][3] >= active_trade.sl:
                        bad_trades += 1
                        available = True
                        active_trade = None
                        print(f"{Fore.RED}{start_dt}, entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")
                    elif temp[-1][2] <= active_trade.tp:
                        good_trades += 1
                        available = True
                        active_trade = None
                        print(f"{Fore.GREEN}{start_dt}, entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")

            if resp and available:
                trade = Checker(exchange, capital=100)
                trade.symbol = symbol
                trade.signal = resp['signal']
                trade.leverage = 5
                if len(temp[-1]) < 4:
                    temp.pop(-1)
            # print(temp[-1])
                trade.entry_price = temp[-1][4]
                trade.reward = 5
                trade.risk = 2.5
                trade.calculate_tp_sl()
                start_dt = datetime.fromtimestamp(temp[-1][0] / 1000)
                print(f"{start_dt}, entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}")        
                active_trade = trade
                available = False
        except IndexError as e:
            print(e)

    return {'good_trade': good_trades, 'bad_trade': bad_trades, 'name': name}


def main():
    symbol = 'TON/USDT:USDT'
    # start_time = datetime(2024, 8, 1, 15, 40)
    # start_ts = datetime.timestamp(start_time)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1000)
    values = {}
    for name in strategies:
        resp = tester(symbol, ohlcv, name)
        # print(resp)
        print(f"       >>>{resp['name']}<<<")
        print(f"========={symbol}==========")
        print(f"Number of good trades => {resp['good_trade']}")
        print(f"Number of bad trades => {resp['bad_trade']}")
        print('=================================\n')
        val = (resp['good_trade'] * 5) - (resp['bad_trade'] * 2.5)
        values[name] = val

    for name, val in values.items():
        print(f"{name} -> {val}")

if __name__ == '__main__':
    main()