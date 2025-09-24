"""
Test configuration and utilities
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.languages.config import LanguageConfig
from src.analyzers.stock_analyzer import StockAnalyzer


class MockStockData:
    """Mock stock data for testing"""
    
    @staticmethod
    def create_sample_data(days=100):
        """Create sample stock data for testing"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
        np.random.seed(42)  # For reproducible tests
        
        # Generate realistic stock price data
        base_price = 100
        returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
        prices = [base_price]
        
        for r in returns[1:]:
            prices.append(prices[-1] * (1 + r))
        
        data = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        return data


class MockStockAnalyzer(StockAnalyzer):
    """Mock analyzer with pre-loaded test data"""
    
    def __init__(self, symbol, test_data=None, lang_config=None):
        """Initialize mock analyzer with test data"""
        self.symbol = symbol.upper()  # Match real StockAnalyzer behavior
        self.data = test_data if test_data is not None else MockStockData.create_sample_data()
        self.lang_config = lang_config if lang_config else LanguageConfig('en')
    
    def fetch_data(self, period="1y"):
        """Override to use mock data"""
        return self.data


class TestConfig:
    """Test configuration constants"""
    TEST_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'TEST']
    SUPPORTED_LANGUAGES = ['en', 'zh']
    SUPPORTED_STRATEGIES = ['technical', 'quantitative', 'ai', 'combined']
    SUPPORTED_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y']


def assert_recommendation_structure(test_case, recommendation):
    """Assert that recommendation has the expected structure"""
    required_keys = [
        'symbol', 'current_price', 'price_change', 'price_change_pct',
        'trend', 'momentum', 'volume', 'recommendation', 'risk_level',
        'analysis_time', 'key_metrics'
    ]
    
    for key in required_keys:
        test_case.assertIn(key, recommendation, f"Missing key: {key}")
    
    # Check recommendation sub-structure
    rec = recommendation['recommendation']
    rec_keys = ['action', 'confidence', 'score', 'signals']
    for key in rec_keys:
        test_case.assertIn(key, rec, f"Missing recommendation key: {key}")
    
    # Check key_metrics sub-structure
    metrics = recommendation['key_metrics']
    metric_keys = ['RSI', 'MACD', 'SMA20', 'SMA50']
    for key in metric_keys:
        test_case.assertIn(key, metrics, f"Missing metric key: {key}")


def assert_valid_recommendation_values(test_case, recommendation):
    """Assert that recommendation values are valid"""
    # Price should be positive
    test_case.assertGreater(recommendation['current_price'], 0)
    
    # RSI should be between 0 and 100
    rsi = recommendation['key_metrics']['RSI']
    test_case.assertGreaterEqual(rsi, 0)
    test_case.assertLessEqual(rsi, 100)
    
    # Score should be between -100 and 100
    score = recommendation['recommendation']['score']
    test_case.assertGreaterEqual(score, -100)
    test_case.assertLessEqual(score, 100)
    
    # Should have analysis signals
    signals = recommendation['recommendation']['signals']
    test_case.assertIsInstance(signals, list)
    test_case.assertGreater(len(signals), 0)
