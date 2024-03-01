#!/usr/bin/python3

from datetime import datetime, timedelta

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



if __name__ == '__main__':
    # changer = Changer()
    # while True:
    #     changer.change()
    #     print(flag)
    #     changer.reset()
    current_dt = datetime(2024, 1, 31, 00, 55, 0)
    print(next(current_dt))