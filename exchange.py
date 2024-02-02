#!/usr/bin/python3

import ccxt


bybit = ccxt.bybit({
    'apiKey': "pUJBHacqf6gG5Y2EvY",
    'secret': "b2GiBTbmYqibPAHVtwQSl6LRZEXtWKuhfzPj",
    'options': {
        'defaultType': 'future'
    }
})

mkt = bybit.load_markets()
