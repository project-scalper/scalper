#!/usr/bin/python3

from datetime import datetime, timedelta
from variables import exchange
import time


flag = False

class Changer():
    def __init__(self):
        pass

    def change(self):
        num = int(input("Enter a number: "))
        global flag
        if num > 5:
            flag = True

    def reset(self):
        global flag
        flag = False

def next(current_dt:datetime):
    next_time = current_dt + timedelta(minutes=5)
    if next_time.minute % 5 != 0:
        minute = next_time.minute - (next_time.minute % 5)
        next_time.replace(minute=minute)
    # else:
    #     minute = next_time.minute

    next_time = next_time.replace(second=0, microsecond=0)

    return next_time

def test_trade(symbol):
    capital = 5
    leverage = 10
    risk = 0.03 * capital
    reward = 0.05 * capital

    exchange.set_leverage(leverage, symbol)
    price = exchange.fetch_ticker(symbol)['last']
    amount = (capital * leverage) / price
    amount = float(exchange.amount_to_precision(symbol, amount))
    cost = amount * price
    maker_fee = exchange.fetch_trading_fee(symbol)['maker'] * amount * price
    taker_fee = exchange.fetch_trading_fee(symbol)['taker'] * amount * price
    tp = (cost + reward + taker_fee + maker_fee) / amount
    sl = (cost - risk + taker_fee + maker_fee) / amount


    params = {
                "takeProfit": {
                    'type': 'limit',
                    'triggerPrice': tp,
                    'price': tp
                },
                'stopLoss': {
                    'type': 'limit',
                    'triggerPrice': sl,
                    'price': sl
                }
            }
    order = exchange.create_order(symbol, 'limit', 'buy', amount, price, params=params)
    print(f"Entry order: {order}")
    time.sleep(2)
    while True:
        entry_order = exchange.fetch_open_order(order['id'], symbol)
        if entry_order['status'] == 'closed':
            print("Order filled!")
            break
        else:
            time.sleep(2)
    orders = exchange.fetch_open_orders(symbol, limit=3)
    for orde in orders:
        if orde['id'] != order['id']:
            if orde['takeProfitPrice']:
                tp_ord = orde
            elif orde['stopLossPrice']:
                sl_ord = orde
    if tp_ord and sl_ord:
        print(f"tp_order: {tp_ord}\nsl_order: {sl_ord}")
    else:
        print("Could not fetch tp and sl orders")
        return
    
    check_till = datetime.now() + timedelta(minutes=2)
    while datetime.now() <= check_till:
        tp_order = exchange.fetch_open_order(tp_ord['id'], symbol)
        sl_order = exchange.fetch_open_order(sl_ord['id'], symbol)
        if tp_order['status'] == 'closed':
            print(f"#{symbol}  -  *TP hit*")
            return
        elif sl_order['status'] == 'closed':
            print(f"#{symbol}  -  *SL hit*")
            return
        else:
            time.sleep(2)

    price = exchange.fetch_ticker(symbol)['last']
    new_order = exchange.edit_order(sl_order['id'], symbol, sl_order['type'],
                                    sl_order['side'], sl_order['amount'], price)
    print(f"New edited order - {new_order}")
    return



if __name__ == '__main__':
    # changer = Changer()
    # while True:
    #     changer.change()
    #     print(flag)
    #     changer.reset()
    current_dt = datetime(2024, 1, 31, 00, 55, 0)
    print(next(current_dt))