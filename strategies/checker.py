#!/usr/bin/python3

from helper.adapter import adapter, trade_logger
from datetime import datetime, timedelta
from variables import risk, reward, capital, leverage
# import asyncio
from strategies.rsi_strategy import active
import time
import ccxt
from helper import watchlist


class Checker():
    capital = capital
    risk = 0.01 * capital
    reward = 0.02 * capital
    leverage = leverage
    # exchange = exchange
    # active = False

    def __init__(self, exchange:ccxt.Exchange, *args, **kwargs):
        self.exchange = exchange
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def calculate_entry_price(self):
        """Calculates the limit entry price for the trade"""
        for i in range(3):
            try:
                last_ohlcv = self.exchange.fetch_ohlcv(self.symbol, '5m', limit=3)
                break
            except:
                if i == 2:
                    adapter.error(f"Error obtaining ohlcv for {self.symbol}")
                    return
                else:
                    continue
        if last_ohlcv:
            self.entry_price = last_ohlcv[1][-2]
        else:
            adapter.warning("Could not obtain entry price for symbol")

    def calculate_tp_sl(self):
        """Calculates takeProfit and stopLoss"""
        if "BUY" in self.signal:
            amount = (self.capital * self.leverage) / self.entry_price
            amount = float(self.exchange.amount_to_precision(self.symbol, amount))
            cost = amount * self.entry_price
            tp = (cost + self.reward) / amount
            sl = (cost - self.risk) / amount

            amount_2 = (self.capital * 5) / self.entry_price
            amount_2 = float(self.exchange.amount_to_precision(self.symbol, amount_2))
            sl_2 = (cost - self.risk) / amount_2

        if "SELL" in self.signal:
            amount = (self.capital * self.leverage) / self.entry_price
            amount = float(self.exchange.amount_to_precision(self.symbol, amount))
            cost = amount * self.entry_price
            tp = (cost - self.reward) / amount
            sl = (cost + self.risk) / amount

            amount_2 = (self.capital * 5) / self.entry_price
            amount_2 = float(self.exchange.amount_to_precision(self.symbol, amount_2))
            sl_2 = (cost + self.risk) / amount_2

        self.tp = float(self.exchange.price_to_precision(self.symbol, tp))
        self.sl = float(self.exchange.price_to_precision(self.symbol, sl))
        self.sl_2
        self.amount = amount
        adapter.info(f"#{self.symbol}. {self.signal} - Entry={self.entry_price}, tp={self.tp}, sl={self.sl}")

    def enter_trade(self):
        if not self.entry_price:
            return
        global active

        valid_till = datetime.now() + timedelta(minutes=5)
        while datetime.now() <= valid_till and active is False:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if ("BUY" in self.signal and ticker['last'] <= self.entry_price) or ("SELL" in self.signal and ticker['last'] >= self.entry_price):
                    self.entry_price = ticker['last']
                    self.calculate_tp_sl()
                    adapter.info(f"#{self.symbol}. {self.signal}. trade entered at {self.entry_price}, tp={self.tp}, sl={self.sl}")
                    active = True
                    self.monitor()
                    active = False
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(2)

        if active is True:
            adapter.info(f"#{self.symbol}. Could not enter trade. Executor already active")
            watchlist.reset(self.symbol)
        else:
            adapter.info(f"#{self.symbol}. {self.signal} - Unable to enter trade in time.")
            watchlist.reset(self.symbol)

    def monitor(self):
        self.start_time = datetime.now()
        self.alerted = False

        while True:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if "BUY" in self.signal:
                    pnl = (ticker['last'] * self.amount) - (self.entry_price * self.amount)
                elif "SELL" in self.signal:
                    pnl = (self.entry_price * self.amount) - (ticker['last'] * self.amount)

                if pnl >= 0.5 * self.reward:
                    self.adjust_sl()

                # if pnl >= self.reward:
                if ("BUY" in self.signal and ticker['last'] >= self.tp) or ("SELL" in self.signal and ticker['last'] <= self.tp):
                    msg = f"#{self.symbol}. signal={self.signal}, start_time={self.start_time}, entry={self.entry_price} "
                    msg += "*TP hit*"
                    trade_logger.info(msg)
                    watchlist.trade_counter(self.signal, "tp")
                    # watchlist.trade_counter(self.symbol, 'tp')
                    watchlist.reset(self.symbol)
                    return
                # elif pnl <= self.risk:
                elif ("BUY" in self.signal and ticker['last'] <= self.sl) or ("SELL" in self.signal and ticker['last'] >= self.sl):
                    msg = f"#{self.symbol}. {self.signal}, start_time={self.start_time}, entry={self.entry_price}, tp={self.tp}, sl={self.sl}, "
                    msg += f"sl_2={self.sl_2}. *SL hit*"
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
                        self.alerted = True
                        if pnl <= 0:
                            watchlist.trade_counter(self.signal, pnl)
                            # watchlist.trade_counter(self.symbol, pnl)
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
        """Calculates maker fee and taker fee"""
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

    async def execute(self, symbol:str, signal:str):
        global active
        if active is True:
            adapter.warning(f"{symbol}. Could not enter trade, executor is currently active")
            return
        self.symbol = symbol
        self.signal = signal

        self.calculate_entry_price()
        self.calculate_tp_sl()
        self.enter_trade()

    def reset(self):
        global active
        active = False
        delattr(self, "symbol")
        delattr(self, "signal")
