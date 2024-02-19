#!/usr/bin/python3

capital = 100
risk = 1.5
reward = 1
leverage = 10
timeframe = '5m'

from exchange import bybit as exchange
print("loading markets...")
exchange = exchange
