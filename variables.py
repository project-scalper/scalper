#!/usr/bin/python3

capital = 100
risk = 0.05       # % of the capital
reward = 0.05     # % of the capital
lev = 5
timeframe = '5m'
confirmation_timeframe = '15m'
reward_risk = 1
daily_target = 0.05
daily_loss = 0.2
time_fmt = "%b %d %Y, %I:%M:%S %p"

from exchange import bybit as exchange
exchange = exchange
