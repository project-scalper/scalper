#!/usr/bin/python3
from exchange import bybit as exchange
from typing import List
import ccxt


class Executor:
    leverage = 5
    capital = 100
    reward = 2
    risk = 1

    def __init__(self, exchange:ccxt.Exchange):
        self.exchange = exchange
        pass

    def set_leverage(self, symbol:str, value:int):
        try:
            self.exchange.set_leverage(value, symbol)
        except Exception as e:
            print(e)

    def execute(self, symbol:str, signal:str, ohlcv:List=[]):
        if signal == "STRONG_BUY":
            entry_price = ohlcv[1][-2]
            amount = self.capital / entry_price
            amount = exchange.amount_to_precision(symbol, amount)

            # calculate tp price
            profit = (self.reward * self.capital) / 100
            tp_price = (profit + (self.leverage * self.capital)) / amount

            # calculate sl price
            loss = (self.risk * self.capital) / 100
            sl_price = ((self.leverage * self.capital) - loss) / amount

            # place order
            self.set_leverage(symbol, self.leverage)
            params = {
                "takeProfit": {
                    'type': 'limit',
                    'triggerPrice': tp_price,
                    'price': tp_price
                },
                'stopLoss': {
                    'type': 'limit',
                    'triggerPrice': sl_price,
                    'price': sl_price
                }
            }

            exchange.create_order(symbol, type="limit", side='buy',
                                amount=amount, price=entry_price, params=params)
