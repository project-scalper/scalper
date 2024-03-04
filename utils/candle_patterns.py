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

def main(ohlcv:List, signal:str):
    if "BUY" in signal:
        return any([hammer(ohlcv), bullish_engulfing(ohlcv)])
    elif "SELL" in signal:
        return any([inverted_hammer(ohlcv), bearish_engulfing(ohlcv)])
    else:
        return False
