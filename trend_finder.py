#!/usr/bin/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


class TrendLine:
    def __init__(self, ohlcv_data):
        """ Initialize the class with OHLCV data.
        ohlcv_data: pandas DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        self.data = ohlcv_data

    def detect_trend(self, window_size=20):
        """
        Detect trends by calculating linear regression on rolling windows.
        window_size: the number of periods to use for calculating trends
        """
        # Calculate rolling min and max for the trend lines
        self.data['rolling_min'] = self.data['low'].rolling(window=window_size).min()
        self.data['rolling_max'] = self.data['high'].rolling(window=window_size).max()

        self.data.dropna(inplace=True)
        
        # Perform linear regression to calculate the trend lines
        self.data['trend_low'] = self._calculate_trend(self.data.index, self.data['rolling_min'])
        self.data['trend_high'] = self._calculate_trend(self.data.index, self.data['rolling_max'])

    def _calculate_trend(self, x, y):
        """
        Apply linear regression to get trend line values.
        """
        x_reshaped = np.array(x).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x_reshaped, y)
        return model.predict(x_reshaped)

    def plot_trends(self):
        """
        Plot the close prices along with the trend lines.
        """
        plt.figure(figsize=(12, 6))
        plt.plot(self.data['close'], label='Close Price', color='blue')
        plt.plot(self.data.index, self.data['trend_low'], label='Support Trendline', color='green')
        plt.plot(self.data.index, self.data['trend_high'], label='Resistance Trendline', color='red')
        plt.title('Crypto Price with Trend Lines')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.show()

# Example usage:
# ohlcv_data = pd.DataFrame({
#     'timestamp': [...],
#     'open': [...],
#     'high': [...],
#     'low': [...],
#     'close': [...],
#     'volume': [...]
# })
# bot = TrendLine(ohlcv_data)
# bot.detect_trend(window_size=20)
# bot.plot_trends()

def main():
    import ccxt

    gate = ccxt.gate()
    _ = gate.load_markets()

    ohlcv = gate.fetch_ohlcv('SOL/USDT', '5m', limit=120)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    bot = TrendLine(df)
    bot.detect_trend(window_size=25)
    bot.plot_trends()

if __name__ == '__main__':
    main()