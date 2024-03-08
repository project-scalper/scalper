#!/usr/bin/python3

from typing import List


def hammer(ohlcv:List) -> bool:
    """This checks the last three candlesticks for a hammer pattern"""
    for idx in range(-4, -1):
        open:float = ohlcv[idx][1]
        high:float = ohlcv[idx][2]
        low:float = ohlcv[idx][3]
        close:float = ohlcv[idx][4]
        # if "BUY" in signal:
        if not ((ohlcv[idx - 1][1] > ohlcv[idx - 1][4]) and (ohlcv[idx + 1][1] < ohlcv[idx + 1][4])):
            continue

        # check the upper and lower wick
        if open < close:    # candle is green
            body_length = close - open
            upper_wick = high - close
            lower_wick = open - low
            if (upper_wick <= (body_length * 0.3)) and (lower_wick >= (2 * body_length)):
                return True
        elif open > close:  # candle is red
            body_length = open - close
            upper_wick = high - open
            lower_wick = close - low
            if (upper_wick <= (body_length * 0.3)) and (lower_wick >= (2 * body_length)):
                return True
        else:
            lower_wick = open - low
            upper_wick = high - open
            if lower_wick >= 3 * upper_wick:
                return True
    return False

def bullish_engulfing(ohlcv:List) -> bool:
    """this checks the last three candlesticks for a bullish engulfing pattern"""
    for idx in range(-4, -1):   # last candle is omitted cause it is not yet closed
        open = ohlcv[idx][1]
        high = ohlcv[idx][2]
        low = ohlcv[idx][3]
        close = ohlcv[idx][4]

        if ohlcv[idx - 1][1] > ohlcv[idx - 1][4]:   # previous candle is red
            prev_length = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
            if open < close:   # current candle is green
                current_length = close - open
                if (close > ohlcv[idx - 1][2]) and (low < ohlcv[idx - 1][3]):
                    if ohlcv[idx - 2][1] > ohlcv[idx - 2][4]:   # the candle before the pattern is bearish
                        return True
                
    return False

def inverted_hammer(ohlcv:List) -> bool:
    """this identifies an inverted hammer pattern"""
    for idx in range(-4, -1):
        open:float = ohlcv[idx][1]
        high:float = ohlcv[idx][2]
        low:float = ohlcv[idx][3]
        close:float = ohlcv[idx][4]
        
        # check if prev candle is green and next candle is red
        if not ((ohlcv[idx - 1][4] > ohlcv[idx - 1][1]) and (ohlcv[idx + 1][4] < ohlcv[idx + 1][1])):
            continue

        # check the upper and lower wick
        if open < close:    # green candle
            body_length = close - open
            upper_wick = high - close
            lower_wick = open - low
            if (lower_wick <= (upper_wick * 0.3)) and (upper_wick >= (2 * body_length)):
                return True
        elif open > close:  # red candle
            body_length = open - close
            upper_wick = high - open
            lower_wick = close - low
            if (lower_wick <= (upper_wick * 0.3)) and (upper_wick >= (2 * body_length)):
                return True
        else:
            lower_wick = open - low
            upper_wick = high - open
            if lower_wick >= 3 * upper_wick:
                return True
    return False

def bearish_engulfing(ohlcv:List) -> bool:
    """This checks the last three candlesticks for a bearish engulfing pattern"""
    for idx in range(-4, -1):
        open = ohlcv[idx][1]
        high = ohlcv[idx][2]
        low = ohlcv[idx][3]
        close = ohlcv[idx][4]

        if ohlcv[idx - 1][4] > ohlcv[idx - 1][1]:   # previous candle is green
            prev_length = ohlcv[idx - 1][4] - ohlcv[idx - 1][1]
            if close < open:   # current candle is red
                current_length = open - close
                if (close < ohlcv[idx - 1][3]) and (high > ohlcv[idx - 1][2]):
                    if ohlcv[idx - 2][1] < ohlcv[idx - 2][4]:   # the candle before the pattern is green
                        return True
    return False

def morning_star(ohlcv:List) -> bool:
    """This searches for the morning star pattern for a bullish reversal"""
    for idx in range(-4, -1):
        # ensure the previous candle is red
        if ohlcv[idx - 1][4] > ohlcv[idx - 1][1]:
            continue
        prev_length = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
        # ensure the next candle is green and has a body longer than halp of the previous candle
        if ohlcv[idx + 1][4] < ohlcv[idx + 1][1]:
            continue
        next_length = ohlcv[idx + 1][4] - ohlcv[idx + 1][1]
        if next_length < prev_length * 0.5:
            continue
        # ensure the current candle has a small body
        if abs(ohlcv[idx][4] - ohlcv[idx][1]) > prev_length * 0.3:
            continue
        return True
    return False

def evening_star(ohlcv:List) -> bool:
    """This searches for the evening star pattern for a bearish reversal pattern"""
    for idx in range(-4, -1):
        # ensure the previous candle is green
        if ohlcv[idx - 1][1] > ohlcv[idx - 1][4]:
            continue
        prev_length = ohlcv[idx - 1][4] - ohlcv[idx - 1][1]
        # ensure the next candle is red
        if ohlcv[idx - 1][4] > ohlcv[idx - 1][1]:
            continue
        next_length = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
        if next_length < prev_length * 0.5:
            continue
        # ensure the current candle has a small body
        if abs(ohlcv[idx][1] - ohlcv[idx][4]) > prev_length * 0.3:
            continue
        return True
    return False

def three_white_soldiers(ohlcv:List) -> bool:
    """This searches for the pattern for a possible bullish reversal"""
    for idx in range(-4, -1):
        # ensure the first candle first candle is green
        if ohlcv[idx - 2][4] < ohlcv[idx - 2][1]:
            continue
        length_1 = ohlcv[idx - 2][4] - ohlcv[idx - 2][1]
        # ensure the second candle is also green and longer than half of the first candle
        if ohlcv[idx - 1][4] < ohlcv[idx - 1][1]:
            continue
        length_2 = ohlcv[idx - 1][4] - ohlcv[idx - 1][1]
        if length_2 < length_1:
            continue
        # ensure the third candle is green and as long as the second
        if ohlcv[idx][4] < ohlcv[idx][1]:
            continue
        length_3 = ohlcv[idx][4] - ohlcv[idx][1]
        if length_3 < length_2:
            continue
        return True
    return False

def black_crows(ohlcv:List) -> bool:
    """This searches for the pattern for a possible bearish reversal"""
    for idx in range(-4, -1):
        # ensure the first candle is red
        if ohlcv[idx - 2][1] < ohlcv[idx - 2][4]:
            continue
        length_1 = ohlcv[idx - 2][1] - ohlcv[idx - 2][4]
        # ensure the second candle is red and longer than the first candle
        if ohlcv[idx - 1][1] < ohlcv[idx - 1][4]:
            continue
        length_2 = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
        if length_2 < length_1:
            continue
        # ensure the third candle is also red and as long as the second
        if ohlcv[idx][1] < ohlcv[idx][4]:
            continue
        length_3 = ohlcv[idx][1] - ohlcv[idx][4]
        if length_3 < length_2:
            continue
        return True
    return False

def three_inside_up(ohlcv:List) -> bool:
    """This searches for the three inside up bullish reversal pattern"""
    for idx in range(-4, -1):
        # ensure the first candle is red
        if ohlcv[idx - 2][1] < ohlcv[idx - 2][4]:
            continue
        length_1 = ohlcv[idx - 2][1] - ohlcv[idx - 2][4]
        # ensure the second candle is green and longer than half of the first
        if ohlcv[idx - 1][4] < ohlcv[idx - 1][1]:
            continue
        length_2 = ohlcv[idx - 1][4] - ohlcv[idx - 1][1]
        if length_2 < length_1 * 0.5:
            continue
        # ensure the third candle is green and closes above the high of the first candle
        if ohlcv[idx][4] < ohlcv[idx][1]:
            continue
        if ohlcv[idx][4] < ohlcv[idx - 2][2]:
            continue
        return True
    return False

def three_inside_down(ohlcv:List) -> bool:
    """This search for the three inside dow pattern bearish pattern"""
    for idx in range(-4, -1):
        # ensure the first candle is green
        if ohlcv[idx - 2][4] < ohlcv[idx - 2][1]:
            continue
        length_1 = ohlcv[idx - 2][4] - ohlcv[idx - 2][1]
        # ensure the second candle is red and closes above the mid body of the first candle
        if ohlcv[idx - 1][1] < ohlcv[idx - 1][4]:
            continue
        length_2 = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
        if length_2 < length_1 * 0.5:
            continue
        # ensure the third candle is red and closes below the low of the first
        if ohlcv[idx][1] < ohlcv[idx][4]:
            continue
        if ohlcv[idx][4] > ohlcv[idx - 2][3]:
            continue
        return True
    return False


def main(ohlcv:List, signal:str):
    if "BUY" in signal:
        return any([hammer(ohlcv), bullish_engulfing(ohlcv), morning_star(ohlcv),
                    three_white_soldiers(ohlcv), three_inside_up(ohlcv)])
    elif "SELL" in signal:
        return any([inverted_hammer(ohlcv), bearish_engulfing(ohlcv), evening_star(ohlcv),
                    black_crows(ohlcv), three_inside_down(ohlcv)])
    else:
        return False
