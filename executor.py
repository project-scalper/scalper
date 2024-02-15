#!/usr/bin/python3

from strategies.checker import Checker
from helper.adapter import adapter
from helper import watchlist
from datetime import datetime, timedelta
import time


class Executor(Checker):
    active = False

    def __init__(self):
        super().__init__()

    def set_leverage(self, symbol:str, value:int):
        try:
            self.exchange.set_leverage(value, symbol)
            self.exchange.set_margin_mode("isolated", self.symbol)
        except Exception as e:
            print(e)

    def enter_trade(self):
        if not self.entry_price:
            return
        enter_flag = False
        valid_till = datetime.now() + timedelta(minutes=5)
        adapter.info(f"#{self.symbol}. New trade found. Waiting for right entry...")
        self.place_order()
        while datetime.now() <= valid_till:
            try:
                order = self.exchange.fetch_open_orders(self.order['id'], self.symbol)
                if order['status'] == 'closed':
                    self.active = True
                    adapter.info(f"#{self.symbol}. {self.signal} - trade entered")
                    enter_flag = True
                    self.monitor()
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(2)

        if enter_flag is False:
            adapter.info(f"#{self.symbol}. {self.signal} - Unable to enter trade in time.")
            self.exchange.cancel_order(self.order['id'], self.symbol)

        self.reset()
        watchlist.reset(self.symbol)

    def place_order(self):
        self.calculate_entry_price()
        self.calculate_tp_sl()
        self.calculate_fee()

        # place order
        self.set_leverage(self.symbol, self.leverage)
        params = {
            "takeProfit": {
                'type': 'limit',
                'triggerPrice': self.tp,
                'price': self.tp
            },
            'stopLoss': {
                'type': 'limit',
                'triggerPrice': self.sl,
                'price': self.sl
            }
        }

        if "BUY" in self.signal:
            side = 'buy'
        else:
            side = 'sell'

        order = self.exchange.create_order(self.symbol, type="limit", side=side,
                            amount=self.amount, price=self.entry_price, params=params)
        
        self.order = order

    def monitor(self):
        # obtain the order_id of the tp and sl orders
        while True:
            try:
                orders = self.exchange.fetch_orders(self.symbol, limit=3)
                for order in orders:
                    if order['id'] != self.order['id']:
                        if order['stopLossPrice']:
                            sl_order = order
                        elif order['takeProfitPrice']:
                            tp_order = order
                if sl_order and tp_order:
                    break
            except Exception as e:
                adapter.warning(f"#{self.symbol}. Unable to fetch trade - {str(e)}")
            finally:
                time.sleep(2)

        # monitor both the tp and sl orders
        alert = False
        while True:
            try:
                tp_ord = self.exchange.fetch_order(tp_order['id'], self.symbol)
                sl_ord = self.exchange.fetch_order(sl_order['id'], self.symbol)

                sig = watchlist.get(self.symbol)
                if ("BUY" in self.signal and "BUY" not in sig) or ("SELL" in self.signal and "SELL" not in sig):
                    if alert is False:
                        alert = True
                        self.adjust_sl(sl_order)

                if tp_ord['status'] == 'closed':
                    adapter.info(f"#{self.symbol}. {self.signal} - TP hit")
                    return
                elif sl_ord['status'] == 'closed':
                    adapter.info(f"#{self.symbol}. {self.signal} - SL hit")
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(2)

    def adjust_sl(self, order):
        cost = self.amount * self.entry_price
        self.calculate_fee()
        if "BUY" in self.signal:
            new_price = (cost + self.fee) / self.amount
        elif "SELL" in self.signal:
            new_price = (cost - self.fee) / self.amount
        try:
            self.exchange.edit_order(order['id'], self.symbol, 'limit', order['side'], order['amount'],
                                     new_price)
        except Exception as e:
            adapter.error(f"{type(e).__name__} - {str(e)}")

    def reset(self):
        self.active = False

    def execute(self, symbol, signal):
        self.symbol = symbol
        self.signal = signal

        try:
            self.calculate_entry_price()
            self.calculate_tp_sl()
            self.enter_trade()
            self.reset()
            watchlist.reset(self.symbol)
        except Exception as e:
            adapter.error(f"{type(e)} - {str(e)}")
