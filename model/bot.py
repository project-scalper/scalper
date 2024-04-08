#!/usr/bin/python3

import model
import ccxt
from model.base_model import BaseModel

class Bot(BaseModel):
    user_id = ""
    trades = []     # contains all the trades taken in the current day
    today_pnl = 0   # contains the pnl for the current day
    daily_pnl = []  # contains the pnl for each of the last 30 days
    capital = 0     # contains the user's intended capital to start the bot
    balance = 0     # contains the actual usdt balance in the user wallet
    pnl_history = []

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
        if 'pnl_history' not in kwargs:
            self.pnl_history = []
        # self.update_balance()

    def get_exchange(self) -> ccxt.Exchange:
        user = model.storage.get("User", self.user_id)
        exchange = getattr(ccxt, user.exchange)()
        exchange.apiKey = user.keys.get("apiKey")
        exchange.secret = user.keys.get("secret")
        exchange.nonce = ccxt.Exchange.milliseconds
        exchange.enableRateLimit = True
        return exchange

    def update_balance(self):
        exchange = self.get_exchange()
        # user = model.storage.get("User", self.user_id)
        # exchange = getattr(ccxt, user.exchange)()
        # # exchange.options['defaultType'] = 'future'
        # exchange.apiKey = user.keys.get("apiKey")
        # exchange.secret = user.keys.get("secret")
        # exchange.nonce = ccxt.Exchange.milliseconds
        bal = exchange.fetch_balance()['free']
        if "USDT" in bal:
            bal = bal['USDT']
        else:
            bal = 0

        self.balance = bal
        # self.balance = 0
        # self.save()

    def verify_capital(self):
        exchange = self.get_exchange()
        # user = model.storage.get("User", self.user_id)
        # exchange:ccxt.Exchange = getattr(ccxt, user.exchange)()
        # # exchange.options['defaultType'] = 'future'
        # exchange.apiKey = user.keys.get("apiKey")
        # exchange.secret = user.keys.get("secret")
        # exchange.none = ccxt.Exchange.milliseconds

        bal = exchange.fetch_balance()['free']
        bal = bal.get("USDT", 0)
        if bal < self.capital:
            raise Exception("Insufficient balance in wallet.")
        else:
            return True