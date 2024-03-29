#!/usr/bin/python3

from helper.adapter import adapter, trade_logger
from datetime import datetime, timedelta
from variables import risk, reward, capital, leverage, timeframe
from strategies.macd_2 import active
import time
import ccxt
import model
from model.bot import Bot
from helper import watchlist

time_fmt = "%b %d %Y, %I:%M:%S %p"
date_fmt = "%b %d %Y"


class Checker():
    capital:int = capital
    leverage:int = leverage
    bot_id = None

    def __init__(self, exchange:ccxt.Exchange, *args, **kwargs):
        self.exchange = exchange
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

        if self.bot_id:
            self.bot:Bot = model.storage.get("Bot", self.bot_id)
            self.capital = int(self.bot.capital)

        self.risk = self.capital * risk
        self.reward = self.capital * reward

    def calculate_entry_price(self):
        """Calculates the limit entry price for the trade"""
        for i in range(3):
            try:
                ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe, limit=3)
                break
            except Exception as e:
                if i == 2:
                    adapter.error(f"Error obtaining ohlcv for {self.symbol}: {e}")
                    return
                else:
                    continue

        last_ohlcv = ohlcv[-2]
        self.ohlcv = ohlcv
        opn = last_ohlcv[1]
        cls = last_ohlcv[4]
        body_length = max([opn, cls]) - min([opn, cls])

        # Entry should be one-third way of the previous candle body
        if "BUY" in self.signal:
            self.entry_price = cls + (0.30 * body_length)
        else:
            self.entry_price = cls - (0.30 * body_length)

        self.entry_price = float(self.exchange.price_to_precision(self.symbol, self.entry_price))

    def calculate_tp_sl(self):
        """Calculates takeProfit and stopLoss prices"""
        amount = (self.capital * self.leverage) / self.entry_price
        amount = float(self.exchange.amount_to_precision(self.symbol, amount))
        cost = amount * self.entry_price

        if "BUY" in self.signal:
            if hasattr(self, "fee"):
                # cost += self.fee
                tp = (cost + self.fee + self.reward) / amount
                sl = (cost + self.fee_sl - self.risk) / amount
                # sl = (cost - self.fee_sl - self.risk) / amount
            else:
                tp = (cost + self.reward) / amount
                sl = (cost - self.risk) / amount

        elif "SELL" in self.signal:
            if hasattr(self, "fee"):
                # cost -= self.fee
                tp = (cost - self.fee - self.reward) / amount
                sl = (cost - self.fee_sl + self.risk) / amount
                # sl = (cost + self.fee_sl + self.risk) / amount
            else:
                tp = (cost - self.reward) / amount
                sl = (cost + self.risk) / amount

        self.tp = float(self.exchange.price_to_precision(self.symbol, tp))
        self.sl = float(self.exchange.price_to_precision(self.symbol, sl))
        self.amount = amount

    def enter_trade(self):
        if not self.entry_price:
            return
        global active

        valid_till = datetime.now() + timedelta(seconds=150)
        while datetime.now() <= valid_till and active is False:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if ("BUY" in self.signal and ticker['last'] <= self.entry_price) or ("SELL" in self.signal and ticker['last'] >= self.entry_price):
                    self.entry_price = ticker['last']
                    if active is True:
                        break

                    self.calculate_tp_sl()
                    adapter.info(f"#{self.symbol}. {self.signal}. trade entered at {self.entry_price}, tp={self.tp}, sl={self.sl}")
                    active = True
                    self.monitor()
                    active = False
                    return
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}")
            finally:
                time.sleep(1)

        if active is True:
            adapter.info(f"#{self.symbol}. Could not enter trade. Executor already active")
            watchlist.reset(self.symbol)
        else:
            adapter.info(f"#{self.symbol}. {self.signal} - Unable to enter trade in time.")
            watchlist.reset(self.symbol)

    def monitor(self):
        self.start_time = datetime.now()
        self.alerted = False
        watch_till = datetime.now() + timedelta(minutes=25)

        while True:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                if "BUY" in self.signal:
                    pnl:float = (ticker['last'] * self.amount) - (self.entry_price * self.amount)
                elif "SELL" in self.signal:
                    pnl:float = (self.entry_price * self.amount) - (ticker['last'] * self.amount)

                if pnl > 0:
                    pnl -= self.fee
                else:
                    pnl -= self.fee_sl

                # if pnl >= 0.5 * self.reward:
                #     self.close_position()
                if datetime.now() >= watch_till:
                    self.close_position()

                if ("BUY" in self.signal and ticker['last'] >= self.tp) or ("SELL" in self.signal and ticker['last'] <= self.tp):
                    msg = f"#{self.symbol}. {self.signal} - start_time={self.start_time}, entry={self.entry_price}, tp={self.tp}, sl={self.sl}, "
                    msg += "*TP hit*"
                    trade_logger.info(msg)
                    watchlist.trade_counter(self.signal, pnl)
                    watchlist.reset(self.symbol)
                    self.update_bot(pnl)
                    return
                
                elif ("BUY" in self.signal and ticker['last'] <= self.sl) or ("SELL" in self.signal and ticker['last'] >= self.sl):
                    msg = f"#{self.symbol}. {self.signal} - start_time={self.start_time}, entry={self.entry_price}, tp={self.tp}, sl={self.sl}, "
                    msg += "*SL hit*"
                    trade_logger.info(msg)
                    watchlist.trade_counter(self.signal, pnl)
                    watchlist.reset(self.symbol)
                    self.update_bot(pnl)
                    return
                
                if hasattr(self, "close_price"):
                    if ("BUY" in self.signal and ticker['last'] <= self.close_price) or ("SELL" in self.signal and ticker['last'] >= self.close_price):
                        msg = f"#{self.symbol}. {self.signal} - start_time={self.start_time}. pnl={pnl}. "
                        if hasattr(self, 'breakeven_profit'):
                            watchlist.trade_counter(self.signal, self.breakeven_profit)
                            msg += f"profit={pnl}"
                        trade_logger.info(msg)
                        watchlist.reset(self.symbol)
                        self.update_bot(pnl)
                        return
                
                # close position when indicators changes signal
                # sig = watchlist.get(self.symbol)
                # if ("BUY" in self.signal and "BUY" not in sig) or ("SELL" in self.signal and "SELL" not in sig):
                #         watchlist.trade_counter(self.signal, pnl)
                #         watchlist.reset(self.symbol)
                #         msg = f"#{self.symbol}. {self.signal} - Trade closed. start_time={self.start_time}, entry={self.entry_price}, tp={self.tp}, sl={self.sl} last_price={ticker['last']} and pnl={pnl:.3f}"
                #         trade_logger.info(msg)
                #         self.update_bot(pnl)
                #         return

            except ccxt.NetworkError as e:
                adapter.error("Seems the network connection is unstable.")
            except Exception as e:
                adapter.error(f"{type(e).__name__} - {str(e)}. line: {e.__traceback__.tb_lineno}")
            finally:
                time.sleep(1)

    def calculate_fee(self):
        """Calculates maker fee and taker fee"""
        for i in range(3):
            try:
                maker_fee = self.exchange.fetchTradingFee(self.symbol)['maker'] * self.amount * self.entry_price
                taker_fee = self.exchange.fetchTradingFee(self.symbol)['taker'] * self.amount * self.tp
                taker_fee_sl = self.exchange.fetchTradingFee(self.symbol)['taker'] * self.amount * self.sl
                break
            except Exception as e:
                if i == 2:
                    adapter.error(f"Unable to fetch trading fee for {self.symbol}")
                    return

        self.fee:float = maker_fee + taker_fee
        self.fee_sl:float = maker_fee + taker_fee_sl

    def close_position(self):
        cost = self.amount * self.entry_price
        
        if "BUY" in self.signal:
            self.close_price = (cost + self.fee_sl) / self.amount
        elif "SELL" in self.signal:
            self.close_price = (cost - self.fee_sl) / self.amount

    def delete(self):
        del self

    async def execute(self, symbol:str, signal:str, reverse:bool=False):
        global active
        if active is True:
            adapter.warning(f"{symbol}. Could not enter trade, executor is currently active")
            return
        self.symbol = symbol
        if reverse is True:
            if "BUY" in signal:
                self.signal = signal.replace("BUY", "SELL")
            elif "SELL" in signal:
                self.signal = signal.replace("SELL", "BUY")
        else:
            self.signal = signal

        self.calculate_entry_price()
        self.calculate_tp_sl()  # This method is called to get an estimated tp value without fees
        self.calculate_fee()
        self.calculate_tp_sl()  # This method is called again to account for fees

        adapter.info(f"#{self.symbol}. {self.signal} - Entry={self.entry_price}, tp={self.tp}, sl={self.sl}")

        self.enter_trade()

    def reset(self):
        global active
        active = False
        delattr(self, "symbol")
        delattr(self, "signal")

    def update_bot(self, pnl:float, reverse:bool=False):
        current_dt = datetime.now()
        current_dt_str = current_dt.strftime(date_fmt)
        if len(self.bot.daily_pnl) > 0:
            last_dt = int(self.bot.daily_pnl[-1]['date'].split()[1])
        else:
            last_dt = current_dt.day
            self.bot.daily_pnl.append({'date' : current_dt_str, 'msg': 0})

        if last_dt + 1 == current_dt.day:
            self.bot.daily_pnl.append({'date': current_dt_str, 'msg': 0})
            self.bot.today_pnl = 0
            self.bot.trades = []
            self.bot.save()

        if "BUY" in self.signal:
            sig = "LONG"
        elif "SELL" in self.signal:
            sig = "SHORT"

        # pnl *= -1
        # if pnl > 0:
        #     pnl -= self.fee
        # else:
        #     pnl -= self.fee_sl
        # pnl -= max(self.fee_sl, self.fee)

        if reverse is True:
            if pnl > 0:
                pnl += self.fee
            else:
                pnl += self.fee_sl

        dt = datetime.now() + timedelta(hours=1)
        dt = dt.strftime(time_fmt)
        self.bot.trades.append({"date": dt, "msg": f"#{self.symbol.split('/')[0]} ({sig}) =>  {pnl:.2f} USDT"})
        self.bot.today_pnl += pnl
        self.bot.daily_pnl[-1]['msg'] += pnl
        self.bot.pnl_history.append(pnl)
        self.bot.pnl_history = self.bot.pnl_history[-5:]
        self.bot.update_balance()
        self.bot.save()
