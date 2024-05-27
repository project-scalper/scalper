#!/usr/bin/python3

# from strategies.macd import analyser
# from strategies.rsi_strategy import analyser
# from strategies.macd_2 import analyser
# from strategies.psar_ema import analyser
# from strategies.adx_psar import analyser
from strategies.adx_t3 import analyser
from datetime import datetime, timedelta
from helper.adapter import adapter
from variables import exchange
from datetime import datetime, timedelta
from model import storage
from model.bot import Bot
import threading
# import ccxt
# from executor.checker import Checker
from executor.executor import Executor
from itertools import cycle

import asyncio

user_exchanges = {}


async def run_thread(symbol, sig_type, bot_id, stop_loss=None):
    nt = threading.Thread(target=set_event, args=(symbol, sig_type, bot_id, stop_loss))
    nt.start()

def set_event(symbol, signal, bot_id, stop_loss):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(new_checker(symbol, signal, bot_id, stop_loss))

async def new_checker(symbol, sig_type, bot_id, stop_loss):
    # bot:Bot = storage.get("Bot", bot_id)
    # if bot:
        # exc = bot.get_exchange()
    exc = user_exchanges.get(bot_id)
    trade = Executor(exc, bot_id=bot_id)
    await trade.execute(symbol, sig_type, reverse=False, stop_loss=stop_loss, use_rr=False)
    # else:
    #     adapter.info(f"Bot {bot_id} not found")


async def main():
    symbols = ['ADA/USDT:USDT', 'SOL/USDT:USDT', 'DOGE/USDT:USDT', 
               'DOT/USDT:USDT', 'XRP/USDT:USDT', 'MATIC/USDT:USDT',
               'SAND/USDT:USDT', 'GALA/USDT:USDT', 'AVAX/USDT:USDT',
               'APE/USDT:USDT', 'LINK/USDT:USDT', 'NEAR/USDT:USDT']
    # run_to = datetime.now() + timedelta(hours=24)
    mkt = exchange.load_markets()
    for _, bot in storage.all(Bot).items():
        user_exchanges[bot.id] = bot.get_exchange()

    current_day = datetime.now().day
    while True:
        try:
            tasks = [analyser(symbol, exchange) for symbol in symbols]
            adapter.info("Starting analysis...")
            signals = await asyncio.gather(*tasks)
            signals = list(filter(lambda x: x is not None, signals))
            cycled_signal = cycle(signals)
            if len(signals) > 0:
                bots = storage.search("Bot", active=True, available=True)
                today_day = datetime.now().day
                if today_day != current_day:
                    flag = True
                    current_day = today_day
                else:
                    flag = False
                for bot in bots:
                    if bot.id not in user_exchanges:
                        user_exchanges[bot.id] = bot.get_exchange()
                    
                    if flag is True:
                        bot.today_pnl = 0
                        bot.trades = []
                        bot.save()
                        current_day = today_day

                    if getattr(bot, 'target_reached', False) is True and getattr(bot, 'target_date', None) == today_day:
                        continue
                    elif getattr(bot, 'sl_reached', False) is True and getattr(bot, 'sl_date', None) == today_day:
                        continue
                    
                    sig = next(cycled_signal)
                    await run_thread(sig['symbol'], sig['signal'], bot_id=bot.id, stop_loss=sig['stop_loss'])
            adapter.info("Analysis completed.")
        except Exception as e:
            msg = f"{type(e).__name__} - {str(e)}"
            adapter.error(msg)
        finally:
            current_dt = datetime.now()
            next_time = current_dt + timedelta(minutes=5)
            if next_time.minute % 5 != 0:
                minute = next_time.minute - (next_time.minute % 5)
                next_time = next_time.replace(minute=minute)

            next_time = next_time.replace(second=0, microsecond=0)
            while datetime.now() < next_time:
                pass


if __name__ == '__main__':
    current_dt = datetime.now()
    if current_dt.minute >= 55:
        hour = current_dt.hour + 1
        minute = 0
    elif current_dt.minute % 5 > 0:
        minute = current_dt.minute + (5 - (current_dt.minute % 5))
        hour = current_dt.hour

    start_time = datetime(current_dt.year, current_dt.month,
                        current_dt.day, hour, minute, 0)
    if datetime.now() >= start_time:
        asyncio.run(main())
