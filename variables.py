#!/usr/bin/python3

capital = 100
risk = 0.05       # % of the capital
reward = 0.025     # % of the capital
leverage = 10
timeframe = '5m'
confirmation_timeframe = '15m'
safety_factor = 0.2

from exchange import bybit as exchange
exchange = exchange
