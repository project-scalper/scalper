#!/usr/bin/python3

import ccxt


bybit = ccxt.bybit({
    'apiKey': "ATyAQgtjl27jFGO4wq",
    'secret': "34OCq6xVUChtKzoVFd9IQQOjZfJv6eBRavnP",
    'nonce': ccxt.Exchange.milliseconds,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# mkt = bybit.load_markets()
