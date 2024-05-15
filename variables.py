#!/usr/bin/python3

capital = 100
risk = 0.05       # % of the capital
reward = 0.075     # % of the capital
lev = 20
timeframe = '5m'
confirmation_timeframe = '15m'
reward_risk = 1.5

from exchange import bybit as exchange
exchange = exchange
