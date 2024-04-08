#!/usr/bin/python3

import ccxt
from helper.loadenv import handleEnv


bybit = ccxt.bybit({
    'apiKey': handleEnv("bybit_apiKey"),
    'secret': handleEnv("bybit_secret"),
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True
    # 'options': {
    #     'defaultType': 'future'
    # }
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

huobi = ccxt.huobi({
    'apiKey': handleEnv("huobi_apiKey"),
    'secret': handleEnv("huobi_secret"),
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True
})

gate = ccxt.gate({
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True
})

# mkt = bybit.load_markets()
