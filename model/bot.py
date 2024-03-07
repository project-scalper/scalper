#!/usr/bin/python3

import model
import ccxt
from model.base_model import BaseModel
# from strategies.executor import Executor

class Bot(BaseModel):
    user_id = ""
    trades = []
    today_trades = []
    daily_pnl = []
    capital = 0
    balance = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "user_id" not in kwargs:
            raise Exception("Bot must include a user id")
        if 'trades' not in kwargs:
            self.trades = []
        if 'today_trades' not in kwargs:
            self.today_trades = []
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