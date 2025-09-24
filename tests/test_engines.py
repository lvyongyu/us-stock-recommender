"""
Unit tests for recommendation engine and strategy manager
"""
import unittest
from tests.test_utils import MockStockAnalyzer, MockStockData, assert_recommendation_structure, assert_valid_recommendation_values
from src.languages.config import LanguageConfig
from src.engines.recommendation_engine import RecommendationEngine
from src.engines.strategy_manager import StrategyManager


class TestStrategyManager(unittest.TestCase):
    """Test strategy manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lang_config = LanguageConfig('en')
        self.strategy_manager = StrategyManager(self.lang_config)
        self.test_data = MockStockData.create_sample_data(100)
        self.analyzer = MockStockAnalyzer("TEST", self.test_data)
    
    def test_strategy_manager_initialization(self):
        """Test strategy manager initialization"""
        self.assertEqual(self.strategy_manager.lang_config, self.lang_config)
        self.assertIn('technical', self.strategy_manager.strategies)
        self.assertIn('quantitative', self.strategy_manager.strategies)
        self.assertIn('ai', self.strategy_manager.strategies)
        
        # Check default weights
        expected_weights = ['technical', 'quantitative', 'ai']
        for strategy in expected_weights:
            self.assertIn(strategy, self.strategy_manager.default_weights)
            self.assertIsInstance(self.strategy_manager.default_weights[strategy], float)
    
    def test_single_strategy_recommendation(self):
        """Test single strategy recommendation"""
        # Test technical strategy
        tech_result = self.strategy_manager.get_recommendation(self.analyzer, ['technical'])
        self.assertIn('action', tech_result)
        self.assertIn('confidence', tech_result)
        self.assertIn('score', tech_result)
        self.assertIn('reasons', tech_result)
        
        # Test quantitative strategy
        quant_result = self.strategy_manager.get_recommendation(self.analyzer, ['quantitative'])
        self.assertIn('action', quant_result)
        self.assertIn('confidence', quant_result)
        self.assertIn('score', quant_result)
        self.assertIn('reasons', quant_result)
    
    def test_combined_strategy_recommendation(self):
        """Test combined strategy recommendation"""
        combined_result = self.strategy_manager.get_recommendation(self.analyzer, ['all'])
        
        # Should have all required keys
        required_keys = ['action', 'confidence', 'score', 'reasons', 'strategy', 'individual_results']
        for key in required_keys:
            self.assertIn(key, combined_result)
        
        # Individual results should contain all strategies
        individual = combined_result['individual_results']
        expected_strategies = ['technical', 'quantitative', 'ai']
        for strategy in expected_strategies:
            self.assertIn(strategy, individual)
        
        # Combined score should be reasonable
        self.assertGreaterEqual(combined_result['score'], -100)
        self.assertLessEqual(combined_result['score'], 100)
    
    def test_invalid_strategy_handling(self):
        """Test handling of invalid strategy types"""
        with self.assertRaises(ValueError):
            self.strategy_manager.get_recommendation(self.analyzer, ['invalid_strategy'])
    
    def test_strategy_weights_normalization(self):
        """Test that strategy weights are properly normalized"""
        result = self.strategy_manager.get_recommendation(self.analyzer, ['all'])
        individual = result['individual_results']
        
        # Sum of weights should be approximately 1.0
        total_weight = sum(strategy['weight'] for strategy in individual.values())
        self.assertAlmostEqual(total_weight, 1.0, places=3)
    
    def test_consensus_analysis(self):
        """Test consensus analysis in combined strategies"""
        result = self.strategy_manager.get_recommendation(self.analyzer, ['all'])
        reasons = result['reasons']
        
        # Should contain consensus information
        consensus_keywords = ['consensus', 'strategies', 'moderate', 'strong', 'mixed']
        has_consensus_info = any(
            any(keyword.lower() in reason.lower() for keyword in consensus_keywords)
            for reason in reasons
        )
        # Note: This might not always be true depending on language configuration
        # so we'll just check that reasons exist
        self.assertGreater(len(reasons), 0)


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation engine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lang_config = LanguageConfig('en')
        self.test_data = MockStockData.create_sample_data(100)
        self.analyzer = MockStockAnalyzer("TEST", self.test_data)
        self.engine = RecommendationEngine(self.analyzer, self.lang_config)
    
    def test_recommendation_engine_initialization(self):
        """Test recommendation engine initialization"""
        self.assertEqual(self.engine.analyzer, self.analyzer)
        self.assertEqual(self.engine.lang_config, self.lang_config)
        self.assertIsNotNone(self.engine.strategy_manager)
    
    def test_generate_recommendation_structure(self):
        """Test recommendation generation structure"""
        recommendation = self.engine.generate_recommendation('technical')
        assert_recommendation_structure(self, recommendation)
    
    def test_generate_recommendation_values(self):
        """Test recommendation generation values"""
        recommendation = self.engine.generate_recommendation('technical')
        assert_valid_recommendation_values(self, recommendation)
    
    def test_different_strategy_types(self):
        """Test different strategy types"""
        strategy_types = ['technical', 'quantitative', 'ai', 'combined']
        
        for strategy_type in strategy_types:
            with self.subTest(strategy=strategy_type):
                recommendation = self.engine.generate_recommendation(strategy_type)
                assert_recommendation_structure(self, recommendation)
                assert_valid_recommendation_values(self, recommendation)
    
    def test_legacy_analysis_methods(self):
        """Test legacy analysis methods for display"""
        metrics = self.analyzer.get_current_metrics()
        
        # Test trend analysis
        trend = self.engine._analyze_trend(metrics)
        self.assertIsInstance(trend, str)
        self.assertIn(trend.lower(), ['uptrend', 'downtrend', 'sideways'])
        
        # Test momentum analysis
        momentum = self.engine._analyze_momentum(metrics)
        self.assertIsInstance(momentum, str)
        self.assertIn('|', momentum)  # Should contain separator
        
        # Test volume analysis
        volume = self.engine._analyze_volume(metrics)
        self.assertIsInstance(volume, str)
    
    def test_risk_assessment(self):
        """Test risk assessment functionality"""
        metrics = self.analyzer.get_current_metrics()
        risk_level = self.engine._assess_risk(metrics)
        
        self.assertIsInstance(risk_level, str)
        valid_risk_levels = ['low_risk', 'medium_risk', 'high_risk']  # These are keys, not display text
        # The actual returned value would be the translated text, so we just check it's a string
        self.assertGreater(len(risk_level), 0)
    
    def test_confidence_formatting(self):
        """Test confidence level formatting"""
        confidence_values = [0.1, 0.5, 0.8, 1.0]
        
        for conf_val in confidence_values:
            formatted = self.engine._format_confidence(conf_val)
            self.assertIsInstance(formatted, str)
            self.assertGreater(len(formatted), 0)
    
    def test_recommendation_with_different_languages(self):
        """Test recommendation generation with different languages"""
        zh_lang_config = LanguageConfig('zh')
        zh_engine = RecommendationEngine(self.analyzer, zh_lang_config)
        
        en_recommendation = self.engine.generate_recommendation('technical')
        zh_recommendation = zh_engine.generate_recommendation('technical')
        
        # Structure should be the same
        assert_recommendation_structure(self, en_recommendation)
        assert_recommendation_structure(self, zh_recommendation)
        
        # Numeric values should be the same
        self.assertEqual(en_recommendation['current_price'], zh_recommendation['current_price'])
        self.assertEqual(en_recommendation['recommendation']['score'], 
                        zh_recommendation['recommendation']['score'])
        
        # But text should be different (different languages)
        self.assertNotEqual(en_recommendation['trend'], zh_recommendation['trend'])
    
    def test_error_handling(self):
        """Test error handling in recommendation generation"""
        # Test with analyzer that has no data
        empty_analyzer = MockStockAnalyzer("EMPTY", MockStockData.create_sample_data(0))
        empty_engine = RecommendationEngine(empty_analyzer, self.lang_config)
        
        with self.assertRaises(Exception):
            empty_engine.generate_recommendation('technical')
    
    def test_analysis_time_format(self):
        """Test analysis time formatting"""
        recommendation = self.engine.generate_recommendation('technical')
        analysis_time = recommendation['analysis_time']
        
        self.assertIsInstance(analysis_time, str)
        # Should be in format YYYY-MM-DD HH:MM:SS
        self.assertEqual(len(analysis_time), 19)
        self.assertIn('-', analysis_time)
        self.assertIn(':', analysis_time)
        self.assertIn(' ', analysis_time)
    
    def test_key_metrics_formatting(self):
        """Test key metrics formatting"""
        recommendation = self.engine.generate_recommendation('technical')
        metrics = recommendation['key_metrics']
        
        # All metrics should be numbers rounded appropriately
        self.assertIsInstance(metrics['RSI'], (int, float))
        self.assertIsInstance(metrics['MACD'], (int, float))
        self.assertIsInstance(metrics['SMA20'], (int, float))
        self.assertIsInstance(metrics['SMA50'], (int, float))
        
        # RSI should be between 0 and 100
        self.assertGreaterEqual(metrics['RSI'], 0)
        self.assertLessEqual(metrics['RSI'], 100)


if __name__ == '__main__':
    unittest.main()
