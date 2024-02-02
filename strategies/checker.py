#!/usr/bin/python3

from helper.adapter import adapter, trade_logger
from datetime import datetime
from variables import *
import asyncio
from helper import watchlist
from exchange import bybit as exchange

async def checker(strat_type:str, symbol:str, signal:str, risk:float=risk, reward:float=reward):
    if "BUY" in signal:
        last_ohlcv = None
        for _ in range(3):
            try:
                last_ohlcv = exchange.fetch_ohlcv(symbol, '5m', limit=3)
                break
            except:
                adapter.error(f"Error obtaining ohlcv for {symbol}")
        if not last_ohlcv:
            return
        entry_price:float = last_ohlcv[1][-2]
        amount = (capital * leverage) / entry_price
        amount = float(exchange.amount_to_precision(symbol, amount))
        cost = amount * entry_price
        # print(f"Amount:{type(amount)}, leverage:{type(leverage)}, reward:{type(reward)}")
        tp_price = (cost + reward) / amount
        sl_price = (cost - risk) / amount
        adapter.info(f"Checker called with args: {symbol} - {signal} - entry={entry_price} - tp={tp_price} - sl={sl_price}")

        start_time = datetime.now()
        while True:
            try:
                ticker = exchange.fetch_ticker(symbol)
                if ticker['last'] >= tp_price:
                    message = f"{strat_type} - symbol: {symbol}, signal: {signal}, entered_trade_at: {start_time}, entry_price: {entry_price}, *TP hit*"
                    trade_logger.info(message)
                    watchlist.reset_one(symbol)
                    return
                if ticker['last'] <= sl_price:
                    message = f"{strat_type} - symbol: {symbol}, signal: {signal}, entered_trade_at: {start_time}, entry_price: {entry_price}, *SL hit*"
                    trade_logger.warning(message)
                    watchlist.reset_one(symbol)
                    return
                sig = watchlist.get(symbol)
                if 'BUY' not in sig:
                    pnl = (ticker['last'] * amount) - (entry_price * amount)
                    msg = f"{strat_type} - symbol: {symbol}, signal: {signal}, entered_trade_at: {start_time}, entry_price: {entry_price}, *Indicator changed at pnl - {pnl}*"
                    trade_logger.warning(msg)
                    # watchlist.reset_one(symbol)
                    return
            except Exception as e:
                msg = f"{type(e).__name__} - {str(e)}"
                adapter.error(msg)
            finally:
                await asyncio.sleep(2)

    elif "SELL" in signal:
        last_ohlcv = None
        for _ in range(3):
            try:
                last_ohlcv = exchange.fetch_ohlcv(symbol, '5m', limit=3)
                break
            except:
                adapter.error(f"Error obtaining ohlcv for {symbol}")
        if not last_ohlcv:
            return
        entry_price = last_ohlcv[1][-2]
        amount = capital / entry_price
        amount = float(exchange.amount_to_precision(symbol, amount))
        cost = amount * entry_price
        tp_price = (cost - reward) / amount
        sl_price = (cost + risk) / amount

        start_time = datetime.now()
        while True:
            try:
                ticker = exchange.fetch_ticker(symbol)
                if ticker['last'] <= tp_price:
                    message = f"{strat_type} - symbol: {symbol}, signal: {signal}, entered_trade_at: {start_time}, entry_price: {entry_price}, *TP hit*"
                    trade_logger.info(message)
                    watchlist.reset_one(symbol)
                    return
                if ticker['last'] >= sl_price:
                    message = f"{strat_type} - symbol: {symbol}, signal: {signal}, entered_trade_at: {start_time}, entry_price: {entry_price}, *SL hit*"
                    trade_logger.warning(message)
                    watchlist.reset_one(symbol)
                    return
                sig = watchlist.get(symbol)
                if 'SELL' not in sig:
                    pnl = (entry_price * amount) - (ticker['last'] * amount)
                    msg = f"{strat_type} - symbol: {symbol}, signal: {signal}, entered_trade_at: {start_time}, entry_price: {entry_price}, *Indicator changed at pnl - {pnl}*"
                    trade_logger.warning(msg)
                    # watchlist.reset_one(symbol)
                    return
            except Exception as e:
                msg = f"{type(e).__name__} - {str(e)}"
                adapter.error(msg)
            finally:
                await asyncio.sleep(2)

    else:
        if signal == 'NEUTRAL':
            return
        adapter.error("Invalid argument for signal. Set signal to either \"BUY\" or \"SELL\"")

    return
