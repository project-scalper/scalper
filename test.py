#!/usr/bin/python3

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


if __name__ == '__main__':
    changer = Changer()
    while True:
        changer.change()
        print(flag)
        changer.reset()