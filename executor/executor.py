#!/usr/bin/python3

from executor.checker import Checker
from helper.adapter import adapter, trade_logger
from helper import watchlist
import ccxt
from datetime import datetime, timedelta
from variables import daily_target
from typing import Dict
import time
import model


class Executor(Checker):

    def __init__(self, exchange:ccxt.Exchange, bot_id:str=None, *args, **kwargs):
        self.bot_id = bot_id
        super().__init__(exchange, *args, **kwargs)
        self.bot = model.storage.get("Bot", self.bot_id)
        self.daily_target = self.bot.capital * daily_target
        self.max_daily_loss = 0.3 * self.bot.capital

    def set_leverage(self, symbol:str, value:int):
        try:
            self.exchange.set_leverage(value, symbol)
        except:
            pass

        try:
            self.exchange.set_margin_mode("isolated", self.symbol)
        except:
            pass

    def enter_trade(self):
        if not self.entry_price:
            return
        self.start_time = datetime.now()
        valid_till = self.start_time + timedelta(minutes=15)
        adapter.info(f"#{self.symbol}. {self.signal} - New trade found. entry={self.entry_price}, tp={self.tp}, sl={self.sl}")
        while datetime.now() <= valid_till:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if ("BUY" in self.signal and ticker['last'] <= self.entry_price) or ("SELL" in self.signal and ticker['last'] >= self.entry_price):
                    self.entry_price = ticker['last']
                    if self.bot.available is False:
                        break

                    self.calculate_tp_sl()
                    self.place_order()
                    self.bot.available = False
                    self.bot.save()
                    while datetime.now() < valid_till:
                        order = self.exchange.fetch_open_order(self.order['id'], self.symbol)
                        if order['status'] == 'closed':
                            adapter.info(f"#{self.symbol}. {self.signal}. trade entered at {self.entry_price}, tp={self.tp}, sl={self.sl}")
                            self.monitor()
                            self.bot.available = True
                            self.bot.save()
                            return
                        elif order['status'] == 'canceled' or order['status'] == 'rejected':
                            adapter.warning(f"#{self.symbol} - Entry order {order['status']}")
                            self.bot.available = True
                            self.bot.save()
                            return
                        else:
                            time.sleep(1)
                    
                    try:
                        self.exchange.cancel_order(order['id'], self.symbol)
                        self.bot.available = True
                        self.bot.save()
                    except Exception as e:
                        adapter.warning(f"Unable to close order for bot {self.bot.id}")
                        return
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(1)

        if self.bot.available is True:
            adapter.info(f"#{self.symbol}. Could not enter trade. Bot {self.bot.id} already in a trade")
        else:
            adapter.info(f"#{self.symbol}. {self.signal} - Unable to enter trade in time.")
        # watchlist.reset(self.symbol)

    def place_order(self):
        # place order
        self.set_leverage(self.symbol, self.leverage)
        params = {
            "takeProfit": {
                'type': 'market',
                'triggerPrice': self.tp,
                # 'price': self.tp
            },
            'stopLoss': {
                'type': 'market',
                'triggerPrice': self.sl,
                # 'price': self.sl
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
                since = int(self.start_time.timestamp())
                orders = self.exchange.fetch_open_orders(self.symbol, limit=3, since=since)
                if len(orders) < 2:
                    continue

                for order in orders:
                    if order['id'] != self.order['id']:
                        if order['stopLossPrice']:
                            sl_order = order
                        elif order['takeProfitPrice']:
                            tp_order = order
                if sl_order and tp_order:
                    # adapter.info("TP and SL orders fetched!")
                    self.sl_order = sl_order
                    self.tp_order = tp_order
                    break
                else:
                    time.sleep(1)
                    continue
            except Exception as e:
                adapter.warning(f"#{self.symbol}. Unable to fetch trade - {str(e)} line {e.__traceback__.tb_lineno}")
            finally:
                time.sleep(1)

        # monitor both the tp and sl orders
        while True:
            try:
                tp_ord = self.exchange.fetch_open_order(tp_order['id'], self.symbol)
                sl_ord = self.exchange.fetch_open_order(sl_order['id'], self.symbol)

                sig = watchlist.get(self.symbol)
                if self.signal != sig:
                # if ("BUY" in self.signal and "BUY" not in sig) or ("SELL" in self.signal and "SELL" not in sig):
                    # adapter.info("Signal changed!!!")
                    trade_logger.info(f"{self.symbol}. {self.signal} - Trade closed. start_time={self.start_time}")
                    self.adjust_sl()
                    return

                if tp_ord['status'] == 'closed':
                    trade_logger.info(f"#{self.symbol}. {self.signal} - *TP hit*")
                    return
                elif sl_ord['status'] == 'closed':
                    trade_logger.info(f"#{self.symbol}. {self.signal} - *SL hit*")
                    return
                elif tp_ord['status'] == 'canceled' or tp_ord['status'] == 'rejected':
                    adapter.warning(f"#{self.symbol}. TP order has been {tp_ord['status']}")
                    return
                elif sl_ord['status'] == 'canceled' or sl_ord['status'] == 'rejected':
                    adapter.warning(f"#{self.symbol}. SL order has been {sl_ord['status']}")
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}. Line {e.__traceback__.tb_lineno}")
            finally:
                if hasattr(self, "psar"):
                    new_sl = watchlist.psar_get(self.symbol)
                    if new_sl != self.sl_order['price']:
                        self.adjust_sl(new_sl)
                time.sleep(1)

    def adjust_sl(self, new_price:float=None):
        """This closes the position or adjusts the stoploss order
        If new_price is given"""

        # cancel the existing sl order
        try:
            self.exchange.cancel_order(self.sl_order['id'], self.symbol)
        except Exception as e:
            adapter.warning(f"Unable to close order for bot {self.bot.id}")
            return

        # create a new limit order
        try:
            new_order = self.exchange.create_order(self.symbol, type='market', side=self.sl_order['side'],
                                       amount=self.amount)
        except Exception as e:
            adapter.warning(f'Unable to create new sl order for bot {self.bot.id}')
            return
        while True:
            sl_order = self.exchange.fetch_open_order(new_order['id'], self.symbol)
            if sl_order['status'] == 'closed':
                return
            elif sl_order['status'] == 'canceled' or sl_order['status'] == 'rejected':
                adapter.warning(f"New sl order was {sl_order['status']} for bot {self.bot.id}")
                return
            else:
                time.sleep(1)

    async def execute(self, symbol, signal, stop_loss=None, reverse:bool=False, use_rr:bool=True):
        self.symbol = symbol
        # self.signal = signal

        self.reverse = reverse
        if stop_loss is None:
            self.psar = watchlist.psar_get(self.symbol)
        else:
            self.stop_loss = stop_loss

        self.use_rr = use_rr

        if reverse is True:
            if "BUY" in signal:
                self.signal = signal.replace("BUY", "SELL")
            elif "SELL" in signal:
                self.signal = signal.replace("SELL", "BUY")
        else:
            self.signal = signal
        
        if "CROSS" in self.signal:
            self.safety_factor /= 3

        try:
            self.calculate_entry_price()
            self.calculate_leverage()
            self.calculate_fee()

            # fetch start balance
            for i in range(3):
                start_balance = self.exchange.fetch_balance()['free'].get("USDT", 0)
                if start_balance != 0:
                    break
                if i == 2:
                    adapter.info(f"Unable to fetch start balance for bot {self.bot.id}")
                    start_balance = self.bot.balance
                else:
                    time.sleep(0.5)

            self.set_leverage(self.symbol, self.leverage)

            adapter.info(f"#{self.symbol}. {self.signal} - Entry={self.entry_price}, tp={self.tp}, sl={self.sl}, leverage={self.leverage}")

            self.enter_trade()

            # fetch end balance
            for i in range(3):
                end_balance = self.exchange.fetch_balance()['free'].get("USDT", 0)
                if end_balance != 0:
                    break
                if i == 2:
                    adapter.info(f"Unable to fetch end balance for ")
            pnl = end_balance - start_balance
            if pnl != 0:
                self.update_bot(pnl)
            if self.bot.today_pnl >= self.daily_target:
                setattr(self.bot, "target_reached", True)
                setattr(self.bot, "target_date", datetime.now().day)
                self.bot.save()
            if self.bot.today_pnl <= self.max_daily_loss * -1:
                setattr(self.bot, "sl_reached", True)
                setattr(self.bot, "sl_date", datetime.now().day)
                self.bot.save()
        except Exception as e:
            adapter.error(f"{type(e).__name__} - {str(e)}, line {e.__traceback__.tb_lineno}")
        return
