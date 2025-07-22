from model import storage
from typing import List


async def fetch_eligible_users()->List:
    # cap = opp['min_cap']
    # eligible_users = {}
    users = storage.all("User")
    eligible_users = [user for _, user in users.items()]
    # for _, user in users.items():
    #     subscribe_stat = await check_user_subscribe_status(user)
    #     trial_stat = await check_user_free_trial_status(user)
    #     if subscribe_stat is True or trial_stat is True:
    #         if user.min_cap >= cap:
    #             net_profit = ((user.min_cap / opp['buy_price']) * opp['sell_price']) - opp['total_fee'] - user.min_cap
    #             profit_percent = (net_profit / user.min_cap) * 100
    #             eligible_users[user.id] = (profit_percent, user.min_cap)
    return eligible_users