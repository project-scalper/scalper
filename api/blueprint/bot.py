#!/usr/bin/python3

from flask import jsonify, request
from main import main
import asyncio
import threading
# from exchange import huo as exchange
from variables import exchange
from model.bot import Bot
from model import storage
from helper import watchlist
from datetime import datetime
from api.blueprint import app_views, auth


def start_scalper(start_time):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # await asyncio.run(main)
    while datetime.now() < start_time:
        pass
    loop.run_until_complete(main())

@app_views.route('/start_checker')
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
    return jsonify("You have started the checker"), 200

@app_views.route('/create_bot', strict_slashes=False)
@auth.login_required
def create_bot():
    user = auth.current_user()
    bot = Bot(user_id=user.id, capital=user.capital)
    # try:
    #     bot.verify_capital()
    # except Exception as e:
    #     return jsonify(e), 400
    bot.save()
    setattr(user, "has_bot", True)
    setattr(user, 'bot_id', bot.id)
    try:
        user.save()
    except Exception as e:
        return jsonify(str(e)), 400
    return jsonify("Your bot has been created successfully"), 200

@app_views.route('/bot/<bot_id>', strict_slashes=False)
@auth.login_required
def get_bot(bot_id):
    if bot_id == 'me':
        user = auth.current_user()
        bot_id = user.bot_id
    bot = storage.get("Bot", bot_id)
    if not bot:
        return jsonify("You have no active bot"), 404
    return jsonify(bot.to_dict()), 200

@app_views.route('/bot', methods=['PUT'], strict_slashes=False)
@auth.login_required
def update_bot():
    user = auth.current_user()
    bot = storage.get("Bot", user.bot_id)
    if not bot:
        return jsonify("Bot not found"), 404
    if not request.json:
        return jsonify("Not a valid json"), 400
    data = request.get_json()
    for key, val in data.items():
        setattr(bot, key, val)
    bot.save()
    return jsonify("Bot updated successfully"), 200
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8002, debug=False)