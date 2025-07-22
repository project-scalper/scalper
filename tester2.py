#!/usr/bin/python3

import asyncio
from variables import timeframe, exchange, reward, risk, capital
from datetime import datetime
from strategies.psar_ema import analyser as psar_ema
from executor.checker import Checker
from colorama import Fore
from typing import Dict, List
import threading


strategies = {'psar_ema': psar_ema}

async def tester(symbol, _ohlcv=None, name="", cap=0):
    if _ohlcv is None:
        _ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1000)
    analyser = strategies[name]
    # print("running tester2...")

    try:
        resp = await analyser(symbol, exchange, _ohlcv)
        if resp:
            print(resp, '24')
            trade = Checker(exchange, capital=cap, symbol=symbol, signal=resp.get('signal'))
            return trade
    except Exception as e:
        print(e)
        print(e.__traceback__.tb_lineno)
        return None

async def main():
    symbols = ['SOL/USDT:USDT', 'DOGE/USDT:USDT', 'LINK/USDT:USDT', 'ADA/USDT:USDT', 
               'GALA/USDT:USDT']
    active_trades:List[Checker] = []
    trade_capital = capital / 5
    max_active_trades = 3
    candle_per_test = 200

    # fetch ohlcv for the tickers we want to test
    all_ohlcv = {}
    for symbol in symbols:
        ohlcv = exchange.fetch_ohlcv(symbol, '5m', limit=1000)
        all_ohlcv[symbol] = ohlcv

    strat_val = {}
    for name in strategies:
        strat_val[name] = {'good_trades': 0, 'bad_trades': 0, 'pnl': 0}
        print(f"Checking {name}...")

        for n in range(candle_per_test):
            idx = candle_per_test - n

            # first confirm status of active trades
            for trade in active_trades:
                candle = all_ohlcv[trade.symbol][idx]
                start_dt = datetime.fromtimestamp(candle[0] / 1000)
                high, low = candle[2], candle[3]

                if 'BUY' in trade.signal:
                    if high >= trade.tp:
                        print(f"{Fore.GREEN}{start_dt}, {trade.symbol} -> entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")
                        trade.is_open = False
                        strat_val[name]['good_trades'] += 1
                    elif low <= trade.sl:
                        print(f"{Fore.RED}{start_dt}, {trade.symbol} -> entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")
                        trade.is_open = False
                        strat_val[name]['bad_trades'] += 1
                
                elif 'SELL' in trade.signal:
                    if low <= trade.tp:
                        print(f"{Fore.GREEN}{start_dt}, {trade.symbol} -> entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")
                        trade.is_open = False
                        strat_val[name]['good_trades'] += 1
                    elif high >= trade.sl:
                        print(f"{Fore.RED}{start_dt}, {trade.symbol} -> entry={trade.entry_price}, signal={trade.signal}, tp={trade.tp}, sl={trade.sl}{Fore.RESET}")
                        trade.is_open = False
                        strat_val[name]['bad_trades'] += 1
            
            # Remove closed trades
            active_trades = [trd for trd in active_trades if trd.is_open]

            available_slots = max_active_trades - len(active_trades)
            if available_slots == 0:
                continue

            tasks = [tester(symbol, all_ohlcv[symbol][idx:], name, trade_capital) for symbol in symbols]
            result = await asyncio.gather(*tasks, return_exceptions=True)
            result = list(filter(lambda x: x is not None and not isinstance(x, Exception), result))

            for trade in result:
                if available_slots == 0:
                    break
                active_trades.append(trade)
                available_slots -= 1

        val = (strat_val[name]['good_trades'] * reward * trade_capital) - (strat_val[name]['bad_trades'] * risk * trade_capital)
        strat_val[name]['pnl'] = val


    print('\n\nTotal summary')
    for name, val in strat_val.items():
        print(f"{name}...")
        for k, v in val.items():
            print(f'  {k} -> {v}')
        print('--------')

if __name__ == '__main__':
    asyncio.run(main())