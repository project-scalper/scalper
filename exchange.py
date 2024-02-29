#!/usr/bin/python3

import ccxt
from helper.loadenv import handleEnv


bybit = ccxt.bybit({
    'apiKey': handleEnv("bybit_apiKey"),
    'secret': handleEnv("bybit_secret"),
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

binance = ccxt.binance({
    'apiKey': handleEnv("binance_apiKey"),
    'secret': handleEnv("binance_secret"),
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# mkt = bybit.load_markets()
