#!/usr/bin/python3

import json
from helper.adapter import adapter
from variables import reward, risk


class WatchList:
    def __init__(self):
        self.fileName = 'watchlist.json'
        self.counterName = "counter.json"
        try:
            with open(self.fileName) as f:
                self.watchlist = json.load(f)
        except FileNotFoundError:
            self.watchlist = {}

        try:
            with open(self.counterName) as f:
                self.counter = json.load(f)
        except FileNotFoundError:
            self.counter = {'total': {'tp': 0, 'sl': 0, 'close_neg': 0}}
        except Exception as e:
            self.counter = {}

    def get(self, symbol:str)->str:
        if symbol in self.watchlist:
            return self.watchlist[symbol]
        else:
            self.watchlist[symbol] = 'NEUTRAL'
            self.__save()
            return 'NEUTRAL'

    def get_all(self):
        return self.watchlist
        
    def __save(self):
        with open(self.fileName, 'w', encoding='utf-8') as fp:
            json.dump(self.watchlist, fp)

    def put(self, symbol:str, signal:str)->bool:
        if "BUY" not in signal and "SELL" not in signal and signal != 'NEUTRAL':
            print(f"#{symbol}. Invalid value for signal {signal}")
            return False
        self.watchlist[symbol] = signal
        # adapter.info(f"{symbol} -> {signal}")
        self.__save()
        return True
    
    def reset(self, symbol:str=None):
        if symbol:
            self.watchlist[symbol] = 'NEUTRAL'
        else:
            for symbol in self.watchlist:
                self.watchlist[symbol] = 'NEUTRAL'
        self.__save()

    def reset_one(self, symbol:str):
        if symbol not in self.watchlist:
            adapter.error("Symbol not found")
            return False
        self.watchlist[symbol] = 'NEUTRAL'
        # adapter.info(f"{symbol} -> NEUTRAL")
        self.__save()
        return True
    
    def reset_all(self):
        for symbol in self.watchlist:
            self.watchlist[symbol] = 'NEUTRAL'
        self.__save()
        # adapter.info("Reset all.")

    def trade_counter(self, signal:str, result):
        if signal not in self.counter:
            self.counter[signal] = {'tp': 0, 'sl': 0, 'close_pos': 0, 'close_neg': 0}
        if result == 'tp' or result == 'sl':
            self.counter[signal][result] += reward
            self.counter['total'][result] += reward
        # elif result == 'sl':
        #     self.counter[signal][result] += risk
        else:
            if result > 0:
                self.counter[signal]['close_pos'] += result
            else:
                self.counter[signal]['close_neg'] += result
        self.counter_save()

    def counter_save(self):
        with open(self.counterName, 'w', encoding='utf-8') as fp:
            json.dump(self.counter, fp)
    
    
# watchlist = WatchList()