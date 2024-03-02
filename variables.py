#!/usr/bin/python3

capital = 100
risk = 0.04 * capital       # 4% of the capital
reward = 0.01 * capital     # 1% of the capital
leverage = 10
timeframe = '5m'

from exchange import bybit as exchange
exchange = exchange
