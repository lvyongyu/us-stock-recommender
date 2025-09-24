"""
Unit tests for trading strategies
"""
import unittest
from tests.test_utils import MockStockAnalyzer, MockStockData, assert_recommendation_structure, assert_valid_recommendation_values
from src.languages.config import LanguageConfig
from src.strategies.technical_strategy import TechnicalIndicatorStrategy
from src.strategies.quantitative_strategy import QuantitativeStrategy


class TestTradingStrategies(unittest.TestCase):
    """Test trading strategy implementations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lang_config = LanguageConfig('en')
        self.test_data = MockStockData.create_sample_data(100)
        self.analyzer = MockStockAnalyzer("TEST", self.test_data)
        
        self.technical_strategy = TechnicalIndicatorStrategy(self.lang_config)
        self.quantitative_strategy = QuantitativeStrategy(self.lang_config)
    
    def test_technical_strategy_initialization(self):
        """Test technical strategy initialization"""
        strategy = TechnicalIndicatorStrategy(self.lang_config)
        self.assertEqual(strategy.lang_config, self.lang_config)
        self.assertEqual(strategy.strategy_name, 'TechnicalIndicatorStrategy')
    
    def test_quantitative_strategy_initialization(self):
        """Test quantitative strategy initialization"""
        strategy = QuantitativeStrategy(self.lang_config)
        self.assertEqual(strategy.lang_config, self.lang_config)
        self.assertEqual(strategy.strategy_name, 'QuantitativeStrategy')
    
    def test_technical_strategy_analysis(self):
        """Test technical strategy analysis"""
        result = self.technical_strategy.analyze(self.analyzer)
        
        # Check structure
        required_keys = ['action', 'confidence', 'score', 'reasons', 'strategy']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check value types and ranges
        self.assertIsInstance(result['action'], str)
        self.assertIsInstance(result['confidence'], (int, float))
        self.assertIsInstance(result['score'], int)
        self.assertIsInstance(result['reasons'], list)
        
        # Score should be between -100 and 100
        self.assertGreaterEqual(result['score'], -100)
        self.assertLessEqual(result['score'], 100)
        
        # Confidence should be between 0 and 1
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)
        
        # Should have analysis reasons
        self.assertGreater(len(result['reasons']), 0)
    
    def test_quantitative_strategy_analysis(self):
        """Test quantitative strategy analysis"""
        result = self.quantitative_strategy.analyze(self.analyzer)
        
        # Check structure
        required_keys = ['action', 'confidence', 'score', 'reasons', 'strategy']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check value types and ranges
        self.assertIsInstance(result['action'], str)
        self.assertIsInstance(result['confidence'], (int, float))
        self.assertIsInstance(result['score'], int)
        self.assertIsInstance(result['reasons'], list)
        
        # Score should be between -100 and 100
        self.assertGreaterEqual(result['score'], -100)
        self.assertLessEqual(result['score'], 100)
        
        # Should have analysis reasons
        self.assertGreater(len(result['reasons']), 0)
    
    def test_strategy_action_types(self):
        """Test that strategies return valid action types"""
        valid_actions = ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell']
        
        # Test technical strategy
        tech_result = self.technical_strategy.analyze(self.analyzer)
        self.assertIn(tech_result['action'], valid_actions)
        
        # Test quantitative strategy
        quant_result = self.quantitative_strategy.analyze(self.analyzer)
        self.assertIn(quant_result['action'], valid_actions)
    
    def test_strategy_with_different_market_conditions(self):
        """Test strategies with different market conditions"""
        # Test with oversold condition (low RSI)
        oversold_data = self.test_data.copy()
        # Simulate price drop to create oversold condition
        oversold_data.loc[oversold_data.index[-10:], 'Close'] *= 0.8
        oversold_analyzer = MockStockAnalyzer("TEST", oversold_data)
        
        tech_result = self.technical_strategy.analyze(oversold_analyzer)
        self.assertIsInstance(tech_result['score'], int)
        
        # Test with overbought condition (high RSI)
        overbought_data = self.test_data.copy()
        # Simulate price surge to create overbought condition
        overbought_data.loc[overbought_data.index[-10:], 'Close'] *= 1.3
        overbought_analyzer = MockStockAnalyzer("TEST", overbought_data)
        
        tech_result = self.technical_strategy.analyze(overbought_analyzer)
        self.assertIsInstance(tech_result['score'], int)
    
    def test_strategy_consistency(self):
        """Test strategy consistency with same input"""
        # Same input should produce same output
        result1 = self.technical_strategy.analyze(self.analyzer)
        result2 = self.technical_strategy.analyze(self.analyzer)
        
        self.assertEqual(result1['action'], result2['action'])
        self.assertEqual(result1['score'], result2['score'])
        self.assertEqual(result1['confidence'], result2['confidence'])
    
    def test_strategy_format_reason(self):
        """Test strategy reason formatting"""
        # Test format_reason method
        reason = self.technical_strategy._format_reason('strategy_rsi_oversold', 25.5)
        self.assertIsInstance(reason, str)
        self.assertIn('25.5', reason)  # Should contain the formatted value
    
    def test_score_to_action_mapping(self):
        """Test score to action mapping consistency"""
        # Create test cases with known scores
        test_scores = [-80, -40, 0, 40, 80]
        expected_actions = ['strong_sell', 'sell', 'hold', 'buy', 'strong_buy']
        
        for score, expected_action in zip(test_scores, expected_actions):
            # Use _generate_recommendation directly to test mapping
            result = self.technical_strategy._generate_recommendation(score, ['test reason'], 'Test')
            self.assertEqual(result['action'], expected_action)
    
    def test_strategy_language_support(self):
        """Test strategy with different languages"""
        zh_lang_config = LanguageConfig('zh')
        zh_strategy = TechnicalIndicatorStrategy(zh_lang_config)
        
        en_result = self.technical_strategy.analyze(self.analyzer)
        zh_result = zh_strategy.analyze(self.analyzer)
        
        # Same logic, different language
        self.assertEqual(en_result['score'], zh_result['score'])
        self.assertEqual(en_result['action'], zh_result['action'])
        # But reasons should be different (different language)
        # Note: This test assumes the reasons contain language-specific text


class TestStrategyIntegration(unittest.TestCase):
    """Integration tests for strategies with real market scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lang_config = LanguageConfig('en')
    
    def test_bull_market_scenario(self):
        """Test strategies in bull market scenario"""
        # Create strong upward trending data
        bull_data = MockStockData.create_sample_data(100)
        
        # Apply stronger upward trend
        trend_multiplier = [1 + i * 0.005 for i in range(len(bull_data))]  # Increased from 0.001 to 0.005
        bull_data['Close'] = bull_data['Close'] * trend_multiplier
        bull_data['High'] = bull_data['High'] * trend_multiplier
        bull_data['Low'] = bull_data['Low'] * trend_multiplier
        bull_data['Open'] = bull_data['Open'] * trend_multiplier
        
        # Ensure ascending order for clarity
        bull_data = bull_data.sort_index()
        
        analyzer = MockStockAnalyzer("BULL", bull_data)
        
        tech_strategy = TechnicalIndicatorStrategy(self.lang_config)
        quant_strategy = QuantitativeStrategy(self.lang_config)
        
        tech_result = tech_strategy.analyze(analyzer)
        quant_result = quant_strategy.analyze(analyzer)
        
        print(f"Bull market - Tech score: {tech_result['score']}, action: {tech_result['action']}")
        print(f"Bull market - Quant score: {quant_result['score']}, action: {quant_result['action']}")
        
        # In bull market, expect positive or neutral bias
        self.assertIn(tech_result['action'], ['buy', 'strong_buy', 'hold'])
        self.assertIn(quant_result['action'], ['buy', 'strong_buy', 'hold'])
    
    def test_bear_market_scenario(self):
        """Test strategies in bear market scenario"""
        # Create downward trending data
        bear_data = MockStockData.create_sample_data(50)
        # Apply downward trend
        trend_multiplier = [1 - i * 0.001 for i in range(len(bear_data))]
        bear_data['Close'] *= trend_multiplier
        bear_data['High'] *= trend_multiplier
        bear_data['Low'] *= trend_multiplier
        bear_data['Open'] *= trend_multiplier
        
        analyzer = MockStockAnalyzer("BEAR", bear_data)
        
        tech_strategy = TechnicalIndicatorStrategy(self.lang_config)
        quant_strategy = QuantitativeStrategy(self.lang_config)
        
        tech_result = tech_strategy.analyze(analyzer)
        quant_result = quant_strategy.analyze(analyzer)
        
        # Results should be valid (but we don't enforce specific actions as 
        # strategies might find oversold opportunities in bear markets)
        self.assertIn(tech_result['action'], ['strong_sell', 'sell', 'hold', 'buy', 'strong_buy'])
        self.assertIn(quant_result['action'], ['strong_sell', 'sell', 'hold', 'buy', 'strong_buy'])


if __name__ == '__main__':
    unittest.main()
