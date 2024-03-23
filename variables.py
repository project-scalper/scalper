#!/usr/bin/python3

capital = 100
risk = 0.015       # % of the capital
reward = 0.01     # % of the capital
leverage = 5
timeframe = '5m'
confirmation_timeframe = '15m'

from exchange import bybit as exchange
exchange = exchange
