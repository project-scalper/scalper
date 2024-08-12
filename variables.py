#!/usr/bin/python3

capital = 100
risk = 0.025       # % of the capital
reward = 0.05     # % of the capital
lev = 5
timeframe = '5m'
confirmation_timeframe = '15m'
reward_risk = 2
daily_target = 0.25
daily_loss = 0.25
time_fmt = "%b %d %Y, %I:%M:%S %p"

from exchange import okx as exchange
exchange = exchange
