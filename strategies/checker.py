#!/usr/bin/python3

from helper.adapter import adapter, trade_logger
from datetime import datetime, timedelta
from variables import risk, reward, exchange, capital, leverage
# import asyncio
import time
import ccxt
from helper import watchlist


class Checker():
    risk = risk
    reward = reward
    capital = capital
    leverage = leverage
    exchange = exchange

    def __init__(self, symbol:str, signal:str, *args, **kwargs):
        self.symbol = symbol
        self.signal = signal
        
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def calculate_entry_price(self):
        for i in range(3):
            try:
                last_ohlcv = self.exchange.fetch_ohlcv(self.symbol, '5m', limit=3)
                break
            except:
                if i == 2:
                    adapter.error(f"Error obtaining ohlcv for {self.symbol}")
                    return
        if last_ohlcv:
            self.entry_price = last_ohlcv[1][-2]
        else:
            adapter.warning("Could not obtain entry price for symbol")

    def calculate_tp_sl(self):
        if "BUY" in self.signal:
            amount = (self.capital * self.leverage) / self.entry_price
            amount = float(self.exchange.amount_to_precision(self.symbol, amount))
            cost = amount * self.entry_price
            tp = (cost + reward) / amount
            sl = (cost - risk) / amount

        if "SELL" in self.signal:
            amount = (self.capital * self.leverage) / self.entry_price
            amount = float(self.exchange.amount_to_precision(self.symbol, amount))
            cost = amount * self.entry_price
            tp = (cost - self.reward) / amount
            sl = (cost + self.risk) / amount

        self.tp = float(self.exchange.price_to_precision(self.symbol, tp))
        self.sl = float(self.exchange.price_to_precision(self.symbol, sl))
        self.amount = amount
        adapter.info(f"#{self.symbol}. {self.signal} - Entry={self.entry_price}, tp={self.tp}, sl={self.sl}")

    def enter_trade(self):
        if not self.entry_price:
            return
        enter_flag = False
        valid_till = datetime.now() + timedelta(minutes=5)
        adapter.info(f"#{self.symbol}. New trade found. Waiting for right entry...")
        while datetime.now() <= valid_till:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if "BUY" in self.signal:
                    if ticker['last'] <= self.entry_price:
                        enter_flag = True
                elif "SELL" in self.signal:
                    if ticker['last'] >= self.entry_price:
                        enter_flag = True
                if enter_flag is True:
                    adapter.info(f"#{self.symbol}. {self.signal}. Now monitoring trade...")
                    self.monitor()
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(2)
        adapter.info(f"#{self.symbol}. {self.signal} - Unable to enter trade in time.")
        watchlist.reset(self.symbol)

    def monitor(self):
        self.start_time = datetime.now()
        self.alerted = False

        while True:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if ("BUY" in self.signal and ticker['last'] >= self.tp) or ("SELL" in self.signal and ticker['last'] <= self.tp):
                    msg = f"#{self.symbol}. signal={self.signal}, start_time={self.start_time}, entry={self.entry_price} "
                    msg += "*TP hit*"
                    trade_logger.info(msg)
                    watchlist.trade_counter(self.signal, "tp")
                    watchlist.reset(self.symbol)
                    return
                elif ("BUY" in self.signal and ticker['last'] <= self.sl) or ("SELL" in self.signal and ticker['last'] >= self.sl):
                    msg = f"#{self.symbol}. signal={self.signal}, start_time={self.start_time}, entry={self.entry_price} "
                    msg += "*SL hit*"
                    trade_logger.info(msg)
                    watchlist.trade_counter(self.signal, 'sl')
                    watchlist.reset(self.symbol)
                    return
                
                if hasattr(self, "close_position"):
                    if ("BUY" in self.signal and ticker['last'] <= self.close_position) or ("SELL" in self.signal and ticker['last'] >= self.close_position):
                        msg = f"#{self.symbol}. {self.signal} - Break-even price hit. start_time={self.start_time}"
                        trade_logger.info(msg)
                        # watchlist.trade_counter(self.signal, 0)
                        watchlist.reset(self.symbol)
                        return
                
                # Raise warning when indicators changes signal
                sig = watchlist.get(self.symbol)
                if ("BUY" in self.signal and "BUY" not in sig) or ("SELL" in self.signal and "SELL" not in sig):
                    if self.alerted is False:
                        if "BUY" in self.signal:
                            pnl = (ticker['last'] * self.amount) - (self.entry_price * self.amount)
                        if "SELL" in self.signal:
                            pnl = (self.entry_price * self.amount) - (ticker['last'] * self.amount)
                        self.alerted = True
                        if pnl <= 0:
                            watchlist.trade_counter(self.signal, pnl)
                            watchlist.reset(self.symbol)
                            msg = f"#{self.symbol}. {self.signal} Trade closed at price={ticker['last']} and pnl={pnl:.3f}, start_time={self.start_time}"
                            trade_logger.info(msg)
                            return
                        else:
                            adapter.info(f"#{self.symbol}. {self.signal} - start_time={self.start_time}. Adjusting stop_loss...")
                            self.adjust_sl()
                        # watchlist.reset(self.symbol)
                        # return

            except ccxt.NetworkError as e:
                adapter.error("Seems the network connection is unstable.")
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(2)

    def calculate_fee(self):
        maker_fee = self.exchange.markets[self.symbol]['maker'] * self.amount * self.entry_price
        taker_fee = self.exchange.markets[self.symbol]['taker'] * self.amount
        self.fee = maker_fee + taker_fee

    def adjust_sl(self):
        cost = self.amount * self.entry_price
        self.calculate_fee()
        if "BUY" in self.signal:
            self.close_position = (cost + self.fee) / self.amount
        elif "SELL" in self.signal:
            self.close_position = (cost - self.fee) / self.amount

    def delete(self):
        del self

    async def execute(self):
        self.calculate_entry_price()
        self.calculate_tp_sl()
        self.enter_trade()
