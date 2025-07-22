#!/usr/bin/python3

import asyncio
from variables import timeframe, exchange, reward, risk, capital, confirmation_timeframe, max_simult_trades
from datetime import datetime, timedelta
# from strategies.adx_t3 import analyser as adx_t3
# from strategies.macd import analyser as macd
# from strategies.macd_2 import analyser as macd2
# from strategies.psar_ema import analyser as psar_ema
# from strategies.adx_psar import analyser as adx_psar
# from strategies.rsi_strategy import analyser as rsi_str
from strategies.atr_boll import analyser as atr_boll
# from strategies.ema_rsi_boll import analyser as ema_rsi
from executor.checker import Checker
from colorama import Fore   # import colour
from typing import Dict
from helper.adapter import adapter
from utils.macd_calculator import macd
import threading
from helper import watchlist


# strategies = {'adx_t3': adx_t3, 'macd': macd, 'psar_ema': psar_ema,
#         'adx_psar': adx_psar, 'rsi_str': rsi_str, 'ema_boll_rsi': ema_rsi}

lock = threading.Lock()
strategies = {"atr_boll": atr_boll}

def tester(symbol, _ohlcv=None, name=""):
    result = {'good_trades': 0, 'bad_trades': 0, 'active_trades': 0, "pnl": 0}
    active_trades = 0
    if not _ohlcv:
        _ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1000)
    analyser = strategies[name]

    def monitor(trade:Checker, since:int, result_dict:Dict):
        # _macd = asyncio.run(macd(exchange, symbol, confirmation_timeframe, ohlcv=lower_ohlcv))
        start_dt = datetime.fromtimestamp(since / 1000)
        # start_monitor = start_dt + timedelta(hours=1)
        # start_monitor_ts = datetime.timestamp(start_monitor) * 1000
        lower_ohlcv = exchange.fetch_ohlcv(trade.symbol, confirmation_timeframe, since=since)

        for _ in range(len(lower_ohlcv)):
            candle = lower_ohlcv.pop(0)
            # macd_ = _macd.pop(0)
            closed_dt = datetime.fromtimestamp(candle[0] / 1000)
            if 'BUY' in trade.signal:
                if candle[2] >= trade.tp:
                    result_dict['good_trades'] += 1

                    print(f"{Fore.GREEN}Entered: {start_dt}\nClosed: {closed_dt}\nEntry: {trade.entry_price}\nSignal: {trade.signal}\nTP: {trade.tp}\nSL: {trade.sl}{Fore.RESET}")
                    
                    watchlist.reset(symbol)
                    pnl = trade.calculate_pnl(trade.tp)
                    print(f"PNL: {pnl}")
                    result_dict['pnl'] += pnl
                    break

                elif candle[3] <= trade.sl:
                    result_dict['bad_trades'] += 1

                    print(f"{Fore.RED}Entered: {start_dt}\nClosed: {closed_dt}\nEntry: {trade.entry_price}\nSignal: {trade.signal}\nTP: {trade.tp}\nSL: {trade.sl}{Fore.RESET}")
                    
                    watchlist.reset(symbol)
                    pnl = trade.calculate_pnl(trade.sl)
                    print(f"PNL: {pnl}")
                    result_dict['pnl'] += pnl
                    break

                # else:
                #     if macd_["MACD"] < 0:
                #         pnl = trade.calculate_pnl(candle[4])
                #         print(f"{Fore.BLUE}Trade closed. PNL: {pnl}{Fore.RESET}")
                #         result_dict['pnl'] += pnl
                #         break


            elif 'SELL' in trade.signal:
                if candle[2] <= trade.tp:
                    result_dict['good_trades'] += 1

                    print(f"{Fore.GREEN}Entered: {start_dt}\nClosed: {closed_dt}\nEntry: {trade.entry_price}\nSignal: {trade.signal}\nTP: {trade.tp}\nSL: {trade.sl}{Fore.RESET}")
                    
                    watchlist.reset(symbol)
                    pnl = trade.calculate_pnl(trade.tp)
                    print(f"PNL: {pnl}")
                    result_dict['pnl'] += pnl
                    break
                elif candle[3] >= trade.sl:
                    result_dict['bad_trades'] += 1
                    
                    print(f"{Fore.RED}Entered: {start_dt}\nClosed: {closed_dt}\nEntry: {trade.entry_price}\nSignal: {trade.signal}\nTP: {trade.tp}\nSL: {trade.sl}{Fore.RESET}")
                    
                    watchlist.reset(symbol)
                    pnl = trade.calculate_pnl(trade.tp)
                    print(f"PNL: {pnl}")
                    result_dict['pnl'] += pnl
                    break
                # else:
                #     if macd_["MACD"] > 0:
                #         pnl = trade.calculate_pnl(candle[4])
                #         print(f"{Fore.BLUE}Trade closed. PNL: {pnl}{Fore.RESET}")
                #         result_dict['pnl'] += pnl
                #         break
            
            result_dict['active_trades'] -= 1
        return

    for n in range(200, len(_ohlcv)):
        try:
            temp = _ohlcv[:n]
            resp = asyncio.run(analyser(symbol, exchange, ohlcv=temp))

            if resp and result['active_trades'] <= max_simult_trades:
                result['active_trades'] += 1
                trade = Checker(exchange, capital=capital, symbol=symbol, signal=resp.get('signal'))
                trade.symbol = symbol
                trade.signal = resp.get('signal')
                trade.leverage = 10
                if len(temp[-1]) < 4:
                    temp.pop(-1)
                trade.entry_price = temp[-1][4]
                trade.reward = reward * capital
                trade.risk = risk * capital
                trade.calculate_tp_sl()
                if "atr" in resp:
                    if "BUY" in trade.signal:
                        trade.sl = trade.entry_price - resp.get("atr")
                        trade.tp = trade.entry_price + (2 * resp.get("atr"))
                    elif "SELL" in trade.signal:
                        trade.sl = trade.entry_price + resp.get("atr")
                        trade.tp = trade.entry_price - (2 * resp.get("atr"))
                    trade.sl = float(trade.exchange.price_to_precision(symbol, trade.sl))
                    trade.tp = float(trade.exchange.price_to_precision(symbol, trade.tp))
                
                thread = threading.Thread(target=monitor, args=[trade, _ohlcv[n][0], result])
                thread.start()
                thread.join()
                active_trades += 1
        except IndexError as e:
            print(e)
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_lineno)

    # return {**result, 'name': name}
    return {'good_trade': result['good_trades'], 'bad_trade': result['bad_trades'], 'pnl': result['pnl'], 'name': name}


def main():
    # symbols = ['SOL', 'DOGE', 'LINK', 'ADA', 'GALA']
    # symbols = ['WAVES', 'APE']
    symbols = [
        'ADA', 'SOL', 'DOGE', 'DOT', 'XRP',
        'SAND', 'GALA', 'AVAX', 'APE', 'LINK', 'NEAR']
    mkt = exchange.load_markets()
    strat_val = {}
    symbol_val = {}
    for name in strategies:
        strat_val[name] = {'good_trades': 0, 'bad_trades': 0, 'pnl': 0}

    for symbol in symbols:
        symbol = symbol + '/USDT:USDT'
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1000)
        values = {}
        for name in strategies:
            try:
                resp = tester(symbol, ohlcv, name)
            except Exception as e:
                print(e)
                print(e.__traceback__.tb_lineno)
                continue
            print(f"       >>>{resp['name']}<<<")
            print(f"========={symbol}==========")
            print(f"Number of good trades => {resp['good_trade']}")
            print(f"Number of bad trades => {resp['bad_trade']}")
            print(f"PNL => {resp['pnl']}")
            print('=================================\n')
            # val = (resp['good_trade'] * reward * capital) - (resp['bad_trade'] * risk * capital)
            val = resp['pnl']
            values[name] = val
            strat_val[name]['good_trades'] += resp['good_trade']
            strat_val[name]['bad_trades'] += resp['bad_trade']
            strat_val[name]['pnl'] += val
            symbol_val[symbol] = {"good_trade": resp['good_trade'], 
                                "bad_trade": resp['bad_trade']}

    print("\n Symbol summary:")
    for symbol, val in symbol_val.items():
        print(f"{symbol}: {val['good_trade']} good trades and {val['bad_trade']} bad trades")

    print('\n\nTotal summary')
    for name, val in strat_val.items():
        print(f"{name}...")
        for k, v in val.items():
            print(f'  {k} -> {v}')
        print('--------')

if __name__ == '__main__':
    main()