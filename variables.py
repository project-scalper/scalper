#!/usr/bin/python3

capital = 100
risk = 0.01 * capital       # 3% of the capital
reward = 0.02 * capital     # 1% of the capital
leverage = 10
timeframe = '5m'
confirmation_timeframe = '15m'

from exchange import bybit as exchange
exchange = exchange
