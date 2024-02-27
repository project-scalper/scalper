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
        if not (ohlcv[idx - 1][1] > ohlcv[idx - 1][4]) and not (ohlcv[idx + 1][1] < ohlcv[idx + 1][4]):
            continue

        # check the upper and lower wick
        if open < close:    # candle is green
            if high <= (close * 1.001):
                body_length = close - open
                if (open - low) >= 2 * body_length:
                    return True
        elif open > close:  # candle is red
            if high <= (open * 1.001):
                body_length = open - close
                if (close - low) >= 2 * body_length:
                    return True
        else:
            low_wick = open - low
            up_wick = high - open
            if low_wick >= 3 * up_wick:
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
                if (current_length >= prev_length) and (high > ohlcv[idx - 1][2]) and (low < ohlcv[idx - 1][3]):
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
        if not (ohlcv[idx - 1][4] > ohlcv[idx - 1][1]) and not (ohlcv[idx + 1][4] < ohlcv[idx + 1][1]):
            continue

        # check the upper and lower wick
        if open < close:    # green candle
            if low >= (open * 0.999):
                body_length = close - open
                if (high - close) >= 2 * body_length:
                    return True
        elif open > close:  # red candle
            if low >= (close * 0.999):
                body_length = open - close
                if (high - open) >= 2 * body_length:
                    return True
        else:
            low_wick = open - low
            up_wick = high - open
            if low_wick >= 3 * up_wick:
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
                if (current_length >= prev_length) and (low < ohlcv[idx - 1][3]) and (high > ohlcv[idx - 1][2]):
                    return True
                
    return False

def main(ohlcv:List, signal:str):
    if "BUY" in signal:
        return any([hammer(ohlcv), bullish_engulfing(ohlcv)])
    elif "SELL" in signal:
        return any([inverted_hammer(ohlcv), bearish_engulfing(ohlcv)])
    else:
        return False