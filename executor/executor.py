#!/usr/bin/python3

from executor.checker import Checker
from helper.adapter import adapter
from helper import watchlist
import ccxt
from datetime import datetime, timedelta
from typing import Dict
import time
import model
from strategies.rsi_strategy import active
# import uuid


class Executor(Checker):
    active = False
    max_daily_loss = 8

    def __init__(self, exchange:ccxt.Exchange, user:Dict, *args, **kwargs):
        self.bot_id = user['bot_id']
        # self.exchange = exchange
        # self.exchange = self.get_exchange(user)
        super().__init__(exchange, *args, **kwargs)
        self.bot = model.storage.get("Bot", self.bot_id)

    def set_leverage(self, symbol:str, value:int):
        try:
            self.exchange.set_leverage(value, symbol)
            self.exchange.set_margin_mode("isolated", self.symbol)
        except:
            pass

    def enter_trade(self):
        if not self.entry_price:
            return
        valid_till = datetime.now() + timedelta(seconds=150)
        adapter.info(f"#{self.symbol}. {self.signal} - New trade found. entry={self.entry_price}, tp={self.tp}, sl={self.sl}")
        # self.place_order()
        global active
        while datetime.now() <= valid_till:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if ("BUY" in self.signal and ticker['last'] <= self.entry_price) or ("SELL" in self.signal and ticker['last'] >= self.entry_price):
                    self.entry_price = ticker['last']
                    if self.active is True:
                        break

                    self.calculate_tp_sl()
                    self.place_order()
                    active = True
                    while True:
                        order = self.exchange.fetch_open_order(self.order['id'], self.symbol)
                        if order['status'] == 'closed':
                            adapter.info(f"#{self.symbol}. {self.signal}. trade entered at {self.entry_price}, tp={self.tp}, sl={self.sl}")
                            self.monitor()
                            break
                        elif order['status'] == 'canceled' or order['status'] == 'rejected':
                            adapter.warning(f"#{self.symbol} - Entry order {order['status']}")
                            break
                        else:
                            time.sleep(1)
                    
                    active = False
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(1)

        if active is True:
            adapter.info(f"#{self.symbol}. Could not enter trade. Executor already active")
        else:
            adapter.info(f"#{self.symbol}. {self.signal} - Unable to enter trade in time.")
        watchlist.reset(self.symbol)

    def place_order(self):
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
        
        while True:
            order = self.exchange.fetch_open_order(order['id'], self.symbol)
            if order['status'] == 'open':
                time.sleep(1)
                continue
            elif order['status'] == 'canceled' or order['status'] == 'rejected':
                adapter.error("Entry order cancelled")
                return False
            elif order['status'] == 'closed':
                self.order = order
                return True
        
    def monitor(self):
        # obtain the  tp and sl orders
        while True:
            try:
                orders = self.exchange.fetch_open_orders(self.symbol, limit=3)
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
                time.sleep(1)

        # monitor both the tp and sl orders
        # alert = False
        while True:
            try:
                tp_ord = self.exchange.fetch_open_order(tp_order['id'], self.symbol)
                sl_ord = self.exchange.fetch_open_order(sl_order['id'], self.symbol)

                # sig = watchlist.get(self.symbol)
                # if ("BUY" in self.signal and "BUY" not in sig) or ("SELL" in self.signal and "SELL" not in sig):
                #     if alert is False:
                #         alert = True
                #         self.close_position()
                #         return

                if tp_ord['status'] == 'closed':
                    adapter.info(f"#{self.symbol}. {self.signal} - *TP hit*")
                    return
                elif sl_ord['status'] == 'closed':
                    adapter.info(f"#{self.symbol}. {self.signal} - *SL hit*")
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                if hasattr(self, "psar"):
                    new_sl = watchlist.psar_get(self.symbol)
                    if new_sl != self.sl_order['price']:
                        self.adjust_sl(new_sl)
                time.sleep(1)

    def adjust_sl(self, new_price:float=None):
        if not new_price:
            new_price = self.exchange.fetch_ticker(self.symbol)['last']
            order_type = 'market'
        else:
            order_type = 'limit'

        for n in range(3):
            try:
                self.exchange.edit_order(self.sl_order['id'], self.symbol, order_type,
                                        self.sl_order['side'], self.amount, new_price,
                                        params={"triggerPrice": new_price})
                break
            except:
                if n == 2:
                    adapter.error(f"#{self.symbol}. Unable to close position")
                    return
                else:
                    time.sleep(1)
        
        # for n in range(3):
        #     try:
        #         self.exchange.edit_order(self.sl_order['id'], self.symbol, 'limit',
        #                                     self.sl_order['side'], self.sl_order['amount'],
        #                                     new_price)
        #         break
        #     except Exception as e:
        #         if n == 2:
        #             adapter.error(f"{type(e).__name__} - {str(e)}")
        #         else:
        #             continue

    async def execute(self, symbol, signal):
        self.symbol = symbol
        self.signal = signal

        try:
            start_balance = self.exchange.fetch_balance()['free'].get("USDT", 0)
            self.calculate_entry_price()
            self.calculate_leverage()
            self.set_leverage(self.symbol, self.leverage)
            self.calculate_tp_sl()
            self.calculate_fee()
            self.calculate_tp_sl()
            self.enter_trade()
            watchlist.reset(self.symbol)
            end_balance = self.exchange.fetch_balance()['free'].get("USDT", 0)
            pnl = end_balance - start_balance
            self.update_bot(pnl)
            return
        except Exception as e:
            adapter.error(f"{type(e)} - {str(e)}")

