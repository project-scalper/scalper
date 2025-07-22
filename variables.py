#!/usr/bin/python3

capital = 100
risk = 0.01       # % of the capital
reward = 0.02     # % of the capital
lev = 10
timeframe = '1h'
confirmation_timeframe = '5m'
max_simult_trades = 4
reward_risk = reward / risk
daily_target = 1
daily_loss = 0.45
time_fmt = "%b %d %Y, %I:%M:%S %p"

from exchange import bybit as exchange
exchange = exchange
