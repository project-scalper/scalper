#!/usr/bin/python3

import model
import ccxt
from model.base_model import BaseModel
# from strategies.executor import Executor

class Bot(BaseModel):
    user_id = ""
    trades = []     # contains all the trades taken in the current day
    today_pnl = 0   # contains the pnl for the current day
    daily_pnl = []  # contains the pnl for each of the last 30 days
    capital = 0
    balance = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "user_id" not in kwargs:
            raise Exception("Bot must include a user id")
        if 'trades' not in kwargs:
            self.trades = []
        if 'today_pnl' not in kwargs:
            self.today_pnl = 0
        if 'daily_pnl' not in kwargs:
            self.daily_pnl = []
        if 'capital' not in kwargs:
            self.capital = 0
        if 'balance' not in kwargs:
            self.balance = 0

        self.update_balance()

    def update_balance(self):
        user = model.storage.get("User", self.user_id)
        exchange = getattr(ccxt, user.exchange)()
        # exchange.options['defaultType'] = 'future'
        exchange.apiKey = user.keys.get("apiKey")
        exchange.secret = user.keys.get("secret")
        exchange.none = ccxt.Exchange.milliseconds
        bal = exchange.fetch_balance()['free']
        if "USDT" in bal:
            bal = bal['USDT']
        else:
            bal = 0

        self.balance = bal
        self.save()

    def verify_capital(self):
        user = model.storage.get("User", self.user_id)
        exchange = getattr(ccxt, user.exchange)()
        # exchange.options['defaultType'] = 'future'
        exchange.apiKey = user.keys.get("apiKey")
        exchange.secret = user.keys.get("secret")
        exchange.none = ccxt.Exchange.milliseconds

        bal = exchange.fetchBalance()['free']
        if "USDT" not in bal:
            raise Exception("Insufficient capital in wallet.")
        bal = bal['USDT']
        if bal < self.capital:
            raise Exception("Insufficient balance in wallet.")