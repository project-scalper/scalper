#!/usr/bin/python3

from typing import List

def is_red(ohlcv: List):
    """Checks if a candlestick is red or not
    Args:
        ohlcv: The ohlcv of the candle to check
    Returns:
        True if candle is red and False if otherwise"""
    if ohlcv[1] > ohlcv[4]:
        return True
    return False

def is_green(ohlcv:List):
    """Checks if a candlestick is green or not
    Args:
        ohlcv: The ohlcv of the candle to check
    Returns:
        True if candle is green and False if otherwise"""
    if ohlcv[4] > ohlcv[1]:
        return True
    return False


def hammer(ohlcv:List) -> bool:
    """This checks the last three candlesticks for a hammer pattern"""
    for idx in range(-4, -1):
        open:float = ohlcv[idx][1]
        high:float = ohlcv[idx][2]
        low:float = ohlcv[idx][3]
        close:float = ohlcv[idx][4]

        if not (is_red(ohlcv[idx - 1]) and is_green(ohlcv[idx + 1])):
            continue

        # check the upper and lower wick
        if is_green(ohlcv[idx]):
            body_length = close - open
            upper_wick = high - close
            lower_wick = open - low
            if (upper_wick <= (body_length * 0.3)) and (lower_wick >= (2 * body_length)):
                return True
        elif is_red(ohlcv[idx]):
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

        if is_red(ohlcv[idx - 1]):
            prev_length = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
            if is_green(ohlcv[idx]):   # current candle is green
                current_length = close - open
                if (close > ohlcv[idx - 1][2]) and (low < ohlcv[idx - 1][3]):
                    if is_red(ohlcv[idx - 2]):
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
        if not (is_red(ohlcv[idx - 1]) and is_green(ohlcv[idx + 1])):
            continue

        # check the upper and lower wick
        if is_green(ohlcv[idx]):
            body_length = close - open
            upper_wick = high - close
            lower_wick = open - low
            if (lower_wick <= (upper_wick * 0.3)) and (upper_wick >= (2 * body_length)):
                return True
        elif is_red(ohlcv[idx]):  # red candle
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

        if is_red(ohlcv[idx - 1]):
            prev_length = ohlcv[idx - 1][4] - ohlcv[idx - 1][1]
            if is_red(ohlcv[idx]):   # current candle is red
                current_length = open - close
                if (close < ohlcv[idx - 1][3]) and (high > ohlcv[idx - 1][2]):
                    if is_green(ohlcv[idx - 2]):
                        return True
    return False

def morning_star(ohlcv:List) -> bool:
    """This searches for the morning star pattern for a bullish reversal"""
    for idx in range(-4, -1):
        # ensure the previous candle is red and the one before it
        if is_green(ohlcv[idx - 1]) or is_green(ohlcv[idx - 2]):
            continue
        prev_length = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
        # ensure the next candle is green and has a body longer than half of the previous candle
        if is_red(ohlcv[idx + 1]):
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
        # ensure the previous candle is green and the one before it
        if not is_green(ohlcv[idx - 2]) or not is_green(ohlcv[idx - 3]):
            continue
        prev_length = ohlcv[idx - 2][4] - ohlcv[idx - 2][1]
        # ensure the next candle is red and is longer than half the prev candle
        if not is_red(ohlcv[idx]):
            continue
        next_length = ohlcv[idx][1] - ohlcv[idx][4]
        if next_length < prev_length * 0.5:
            continue
        # ensure the current candle has a small body
        if abs(ohlcv[idx - 1][1] - ohlcv[idx - 1][4]) > prev_length * 0.3:
            continue
        return True
    return False

def three_white_soldiers(ohlcv:List) -> bool:
    """This searches for the pattern for a possible bullish reversal"""
    for idx in range(-4, -1):
        # ensure the first candle is green and the one before it
        if not is_green(ohlcv[idx - 2]) or not is_green(ohlcv[idx - 3]):
            continue
        length_1 = ohlcv[idx - 2][4] - ohlcv[idx - 2][1]
        # ensure the second candle is also green and longer than the first candle
        if not is_green(ohlcv[idx - 1]):
            continue
        length_2 = ohlcv[idx - 1][4] - ohlcv[idx - 1][1]
        if length_2 < length_1:
            continue
        # ensure the third candle is green and as long as the second
        if not is_green(ohlcv[idx]):
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
        if not is_red(ohlcv[idx - 2]) or not is_red(ohlcv[idx - 3]):
            continue
        length_1 = ohlcv[idx - 2][1] - ohlcv[idx - 2][4]
        # ensure the second candle is red and longer than the first candle
        if not is_red(ohlcv[idx - 1]):
            continue
        length_2 = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
        if length_2 < length_1:
            continue
        # ensure the third candle is also red and as long as the second
        if not is_red(ohlcv[idx]):
            continue
        length_3 = ohlcv[idx][1] - ohlcv[idx][4]
        if length_3 < length_2:
            continue
        return True
    return False

def three_inside_up(ohlcv:List) -> bool:
    """This searches for the three inside up bullish reversal pattern"""
    for idx in range(-4, -1):
        # ensure the first candle is red and the one before it
        if not is_red(ohlcv[idx - 2]) or not is_red(ohlcv[idx - 3]):
            continue
        length_1 = ohlcv[idx - 2][1] - ohlcv[idx - 2][4]
        # ensure the second candle is green and longer than half of the first
        if not is_green(ohlcv[idx - 1]):
            continue
        length_2 = ohlcv[idx - 1][4] - ohlcv[idx - 1][1]
        if length_2 < length_1 * 0.5:
            continue
        # ensure the third candle is green and closes above the high of the first candle
        if not is_green(ohlcv[idx]):
            continue
        if ohlcv[idx][4] < ohlcv[idx - 2][2]:
            continue
        return True
    return False

def three_inside_down(ohlcv:List) -> bool:
    """This search for the three inside dow pattern bearish pattern"""
    for idx in range(-4, -1):
        # ensure the first candle is green and the one before it
        if not is_green(ohlcv[idx - 2]) or not is_green(ohlcv[idx - 3]):
            continue
        length_1 = ohlcv[idx - 2][4] - ohlcv[idx - 2][1]
        # ensure the second candle is red and closes above the mid body of the first candle
        if not is_red(ohlcv[idx - 1]):
            continue
        length_2 = ohlcv[idx - 1][1] - ohlcv[idx - 1][4]
        if length_2 < length_1 * 0.5:
            continue
        # ensure the third candle is red and closes below the low of the first
        if not is_red(ohlcv[idx]):
            continue
        if ohlcv[idx][4] > ohlcv[idx - 2][3]:
            continue
        return True
    return False


def candle_main(ohlcv:List, signal:str):
    if "BUY" in signal:
        return any([hammer(ohlcv), bullish_engulfing(ohlcv), morning_star(ohlcv),
                    three_white_soldiers(ohlcv), three_inside_up(ohlcv)])
    elif "SELL" in signal:
        return any([inverted_hammer(ohlcv), bearish_engulfing(ohlcv), evening_star(ohlcv),
                    black_crows(ohlcv), three_inside_down(ohlcv)])
    else:
        return False
