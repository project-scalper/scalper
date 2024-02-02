#!/usr/bin/python3

import json
from helper.adapter import adapter


class WatchList:
    def __init__(self):
        self.fileName = 'watchlist.json'
        try:
            with open(self.fileName) as f:
                self.watchlist = json.load(f)
        except FileNotFoundError:
            self.watchlist = {}

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
        self.__save()
        return True
    
    def reset_one(self, symbol:str):
        if symbol not in self.watchlist:
            adapter.error("Symbol not found")
            return False
        self.watchlist[symbol] = 'NEUTRAL'
        self.__save()
        return True
    
    def reset_all(self):
        for symbol in self.watchlist:
            self.watchlist[symbol] = 'NEUTRAL'
        self.__save()
    
    
# watchlist = WatchList()