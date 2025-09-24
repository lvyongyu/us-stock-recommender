"""
Unit tests for stock analyzer
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from tests.test_utils import MockStockData, MockStockAnalyzer, TestConfig


class TestStockAnalyzer(unittest.TestCase):
    """Test stock analyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = MockStockData.create_sample_data(100)
        self.analyzer = MockStockAnalyzer("TEST", self.test_data)
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        analyzer = MockStockAnalyzer("aapl")
        self.assertEqual(analyzer.symbol, "AAPL")  # Should be uppercase
        self.assertIsNotNone(analyzer.data)
    
    def test_data_structure(self):
        """Test that mock data has correct structure"""
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            self.assertIn(col, self.test_data.columns)
        
        # Data should have reasonable values
        self.assertTrue((self.test_data['High'] >= self.test_data['Low']).all())
        self.assertTrue((self.test_data['High'] >= self.test_data['Close']).all())
        self.assertTrue((self.test_data['Low'] <= self.test_data['Close']).all())
        self.assertTrue((self.test_data['Volume'] > 0).all())
    
    def test_technical_indicators_calculation(self):
        """Test technical indicators calculation"""
        indicators = self.analyzer.calculate_technical_indicators()
        
        # Check that all expected indicators exist
        expected_indicators = [
            'sma_20', 'sma_50', 'ema_12', 'ema_26', 'macd', 'signal',
            'histogram', 'rsi', 'bb_upper', 'bb_lower', 'volume_sma'
        ]
        
        for indicator in expected_indicators:
            self.assertIn(indicator, indicators)
            self.assertIsInstance(indicators[indicator], pd.Series)
    
    def test_rsi_bounds(self):
        """Test RSI values are within valid bounds"""
        indicators = self.analyzer.calculate_technical_indicators()
        rsi = indicators['rsi'].dropna()
        
        # RSI should be between 0 and 100
        self.assertTrue((rsi >= 0).all())
        self.assertTrue((rsi <= 100).all())
    
    def test_moving_averages(self):
        """Test moving averages are calculated correctly"""
        indicators = self.analyzer.calculate_technical_indicators()
        
        # SMA20 should be the 20-day simple moving average
        expected_sma20 = self.test_data['Close'].rolling(window=20).mean()
        pd.testing.assert_series_equal(indicators['sma_20'], expected_sma20, check_names=False)
        
        # SMA50 should be the 50-day simple moving average
        expected_sma50 = self.test_data['Close'].rolling(window=50).mean()
        pd.testing.assert_series_equal(indicators['sma_50'], expected_sma50, check_names=False)
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        indicators = self.analyzer.calculate_technical_indicators()
        
        bb_upper = indicators['bb_upper']
        bb_lower = indicators['bb_lower']
        sma_20 = indicators['sma_20']
        
        # Upper band should be above SMA, lower band should be below
        comparison_data = pd.DataFrame({
            'upper': bb_upper,
            'sma': sma_20,
            'lower': bb_lower
        }).dropna()
        
        self.assertTrue((comparison_data['upper'] >= comparison_data['sma']).all())
        self.assertTrue((comparison_data['lower'] <= comparison_data['sma']).all())
    
    def test_current_metrics(self):
        """Test current metrics calculation"""
        metrics = self.analyzer.get_current_metrics()
        
        # Check required metrics exist
        required_metrics = [
            'current_price', 'previous_close', 'volume', 'avg_volume',
            'sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal',
            'bb_upper', 'bb_lower', 'price_change', 'price_change_pct'
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], (int, float, np.int64, np.float64))
    
    def test_price_change_calculation(self):
        """Test price change calculation"""
        metrics = self.analyzer.get_current_metrics()
        
        expected_change = metrics['current_price'] - metrics['previous_close']
        self.assertAlmostEqual(metrics['price_change'], expected_change, places=5)
        
        expected_pct = (expected_change / metrics['previous_close']) * 100
        self.assertAlmostEqual(metrics['price_change_pct'], expected_pct, places=3)
    
    def test_volume_metrics(self):
        """Test volume-related metrics"""
        metrics = self.analyzer.get_current_metrics()
        
        # Current volume should be positive
        self.assertGreater(metrics['volume'], 0)
        
        # Average volume should be positive
        self.assertGreater(metrics['avg_volume'], 0)
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_analyzer = MockStockAnalyzer("TEST", pd.DataFrame())
        
        with self.assertRaises(ValueError):
            empty_analyzer.get_current_metrics()
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data for indicators"""
        # Create data with only 10 days (less than needed for some indicators)
        short_data = MockStockData.create_sample_data(10)
        short_analyzer = MockStockAnalyzer("TEST", short_data)
        
        # Should still work but some indicators will have NaN values
        metrics = short_analyzer.get_current_metrics()
        self.assertIsInstance(metrics['current_price'], (int, float, np.int64, np.float64))
        
        # SMA50 should be NaN with only 10 days of data
        self.assertTrue(pd.isna(metrics['sma_50']) or metrics['sma_50'] is None)


if __name__ == '__main__':
    unittest.main()
