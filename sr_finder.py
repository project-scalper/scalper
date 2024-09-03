#!/usr/bin/python3

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import ccxt

exchange = ccxt.bybit()
mkt = exchange.load_markets()

class SupportResistanceZones:
    def __init__(self, ohlcv, threshold=0.01):
        """
        Initialize with OHLCV data.
        
        Parameters:
        - ohlcv: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        - threshold: Price difference threshold for clustering (default 1%)
        """
        self.ohlcv = ohlcv
        self.threshold = threshold
        self.support_zones = []
        self.resistance_zones = []
    
    def calculate_zones(self):
        """Calculate the support and resistance zones."""
        highs = self.ohlcv['high'].values
        lows = self.ohlcv['low'].values
        
        # Find peaks in the highs (resistance) and valleys in the lows (support)
        resistance_peaks, _ = find_peaks(highs)
        support_peaks, _ = find_peaks(-lows)
        
        # Cluster peaks to find zones
        self.resistance_zones = self._find_zones(highs[resistance_peaks])
        self.support_zones = self._find_zones(lows[support_peaks])
    
    def _find_zones(self, levels):
        """Identify zones by clustering levels within the threshold."""
        zones = []
        levels_sorted = np.sort(levels)
        
        current_zone = [levels_sorted[0]]
        
        for level in levels_sorted[1:]:
            if abs(level - current_zone[-1]) <= self.threshold * current_zone[-1]:
                current_zone.append(level)
            else:
                zone_min = min(current_zone)
                zone_max = max(current_zone)
                zones.append((zone_min, zone_max))
                current_zone = [level]
        
        # Append the last zone
        if current_zone:
            zone_min = min(current_zone)
            zone_max = max(current_zone)
            zones.append((zone_min, zone_max))
        
        return zones
    
    def get_support_zones(self):
        """Return the support zones."""
        return self.support_zones
    
    def get_resistance_zones(self):
        """Return the resistance zones."""
        return self.resistance_zones


def main(symbol='APE/USDT:USDT', timeframe='5m', limit=1000):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    ohlcv_df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high',
                        'low', 'close', 'volume'])

    sr_zones = SupportResistanceZones(ohlcv_df)
    sr_zones.calculate_zones()

    support_zones = sr_zones.get_support_zones()
    resistance_zones = sr_zones.get_resistance_zones()

    print("Support Zones:", support_zones)
    print("Resistance Zones:", resistance_zones)
