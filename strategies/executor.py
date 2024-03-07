#!/usr/bin/python3

from strategies.checker import Checker
from helper.adapter import adapter
from helper import watchlist
import ccxt
from datetime import datetime, timedelta
from typing import Dict
import time
import model
import uuid


class Executor(Checker):
    active = False
    max_daily_loss = 8

    def __init__(self, user:Dict):
        self.bot_id = user['bot_id']
        self.exchange = self.get_exchange(user)
        super().__init__(self.exchange)
        self.bot = model.storage.get("Bot", self.bot_id)

    def get_exchange(self, user):
        exchange: ccxt.Exchange = getattr(ccxt, user['exchange'])()
        exchange.apiKey = user['keys']['apiKey']
        exchange.secret = user['keys']['secret']
        exchange.options['defaultType'] = 'future'
        exchange.nonce = ccxt.Exchange.milliseconds
        exchange.enableRateLimit = True
        return exchange

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
        adapter.info(f"#{self.symbol}. New trade found. entry={self.entry_price}, tp={self.tp}, sl={self.sl}")
        # self.place_order()
        while datetime.now() <= valid_till:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if ("BUY" in self.signal and ticker['last'] <= self.entry_price) or ("SELL" in self.signal and ticker['last'] >= self.entry_price):
                    self.entry_price = ticker['last']
                    if active is True:
                        break

                    self.calculate_tp_sl()
                    self.place_order()
                    active = True
                    while True:
                        order = self.exchange.fetch_order(self.order['id'], self.symbol)
                        if order['status'] == 'closed':
                            enter_flag = True
                            adapter.info(f"#{self.symbol}. {self.signal}. trade entered at {self.entry_price}, tp={self.tp}, sl={self.sl}")
                            break
                        else:
                            time.sleep(1)
                    
                    self.monitor()
                    active = False
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(2)

        if enter_flag is False:
            if active is True:
                adapter.info(f"#{self.symbol}. Unable to enter trade, executor is active")
            else:
                adapter.info(f"#{self.symbol}. {self.signal} - Unable to enter trade in time.")
            # self.exchange.cancel_order(self.order['id'], self.symbol)

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

        try:
            order = self.exchange.create_order(self.symbol, type="limit", side=side,
                                amount=self.amount, price=self.entry_price, params=params)
        except Exception as e:
            adapter.error(f"{type(e).__name__} - {str(e)}")
            return
        
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
                    self.sl_order = sl_order
                    self.tp_order = tp_order
                    break
                else:
                    time.sleep(1)
                    continue
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
                    adapter.info(f"#{self.symbol}. {self.signal} - *TP hit*")
                    return
                elif sl_ord['status'] == 'closed':
                    adapter.info(f"#{self.symbol}. {self.signal} - *SL hit*")
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(2)

    def adjust_sl(self, profit:float=0):
        cost = self.amount * self.entry_price
        self.calculate_fee()
        if "BUY" in self.signal:
            new_price = (cost + self.fee + profit) / self.amount
        elif "SELL" in self.signal:
            new_price = (cost - self.fee - profit) / self.amount
        
        for n in range(3):
            try:
                self.exchange.edit_order(self.sl_order['id'], self.symbol, 'limit',
                                            self.sl_order['side'], self.sl_order['amount'],
                                            new_price)
                break
            except Exception as e:
                if n == 2:
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

