#!/usr/bin/python3

import ccxt
# from helper.loadenv import handleEnv


bybit = ccxt.bybit({
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True
})

binance = ccxt.binance({
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

huobi = ccxt.huobi({
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True
})

gate = ccxt.gate({
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True
})

okx = ccxt.okx({
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True
})

