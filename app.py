#!/usr/bin/python3

from flask import Flask
from flask_cors import CORS
from main import main
import asyncio
import threading
from exchange import bybit as exchange
from helper import watchlist
from datetime import datetime


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def start_scalper(start_time):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # await asyncio.run(main)
    while datetime.now() < start_time:
        pass
    loop.run_until_complete(main())

@app.route('/start_checker')
def start_checker():
    mkt = exchange.load_markets()
    current_dt = datetime.now()
    if current_dt.minute >= 55:
        hour = current_dt.hour + 1
        minute = 0
    elif current_dt.minute % 5 > 0:
        minute = current_dt.minute + (5 - (current_dt.minute % 5))
        hour = current_dt.hour
    else:
        minute = current_dt.minute + 5
        hour = current_dt.hour

    start_time = datetime(current_dt.year, current_dt.month,
                        current_dt.day, hour, minute, 0)
    print(f"Waiting...")
    watchlist.reset()

    checker = threading.Thread(target=start_scalper, args=(start_time, ))
    checker.start()
    return "You have started the checker"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=False)