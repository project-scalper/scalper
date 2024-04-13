#!/usr/bin/python3

import model
import ccxt
from model.base_model import BaseModel

class Bot(BaseModel):
    __tablename__ = 'bots'
    
    user_id = None
    trades = []     # contains all the trades taken in the current day
    today_pnl = 0   # contains the pnl for the current day
    daily_pnl = []  # contains the pnl for each of the last 30 days
    capital = 0     # contains the user's intended capital to start the bot
    balance = 0     # contains the actual usdt balance in the user wallet
    pnl_history = []
    active = True
    available = True

    def __init__(self, *args, **kwargs):
        self.user_id = None
        self.trades = []     # contains all the trades taken in the current day
        self.today_pnl = 0   # contains the pnl for the current day
        self.daily_pnl = []  # contains the pnl for each of the last 30 days
        self.capital = 0     # contains the user's intended capital to start the bot
        self.balance = 0     # contains the actual usdt balance in the user wallet
        self.pnl_history = []
        self.active = True
        self.available = True
        
        super().__init__(*args, **kwargs)
        if "user_id" not in kwargs:
            raise Exception("Please include a user id")
        self.update_balance()
        if not hasattr(self, "capital"):
            owner = model.storage.get("User", self.user_id)
            self.capital = float(owner.capital)

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
        bal = exchange.fetch_balance()['free']
        if "USDT" in bal:
            bal = bal['USDT']
        else:
            bal = 0

        self.balance = bal

    def verify_capital(self):
        exchange = self.get_exchange()

        bal = exchange.fetch_balance()['free']
        bal = bal.get("USDT", 0)
        if bal < self.capital:
            raise Exception("Insufficient balance in wallet.")
        else:
            return True