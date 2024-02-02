#!/usr/bin/python3

from helper import watchlist
from variables import exchange
from helper.adapter import adapter
from utils.ema_calculator import ema
from utils.macd_calculator import macd


def monitor(symbol:str, signal:str, sig_type:str):
    if sig_type == 'EMA_ONLY':
        _ema_50 = ema(exchange, symbol, 50)
        _ema_200 = ema(exchange, symbol, 200)
        if signal == 'BUY':
            if _ema_200 > _ema_50:
                watchlist.reset_one(symbol)
        pass