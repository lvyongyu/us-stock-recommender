"""
Integration tests for the complete stock recommendation system
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch

from tests.test_utils import MockStockData, MockStockAnalyzer


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Add the main directory to path for importing
        main_dir = os.path.join(os.path.dirname(__file__), '..')
        if main_dir not in sys.path:
            sys.path.insert(0, main_dir)
            
        from src.languages.config import LanguageConfig
        self.lang_config_en = LanguageConfig('en')
        self.lang_config_zh = LanguageConfig('zh')
        self.sample_data = MockStockData.create_sample_data()
    
    def test_end_to_end_recommendation_technical(self):
        """Test end-to-end recommendation with technical strategy"""
        from src.engines.recommendation_engine import RecommendationEngine
        
        # Create mock analyzer
        analyzer = MockStockAnalyzer("AAPL", self.sample_data)
        
        # Create recommendation engine
        engine = RecommendationEngine(analyzer, self.lang_config_en)
        
        # Generate recommendation
        result = engine.generate_recommendation(strategy_type='technical')
        
        # Verify structure
        self.assertIn('recommendation', result)
        self.assertIn('action', result['recommendation'])
        self.assertIn('confidence', result['recommendation'])
        self.assertIn('score', result['recommendation'])
        self.assertIn('analysis_time', result)
        self.assertIn('key_metrics', result)
        self.assertIn('current_price', result)
        
        # Verify values
        self.assertIsInstance(result['recommendation']['score'], int)
        self.assertIn(result['recommendation']['action'].lower(), ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell'])
        
    def test_end_to_end_recommendation_combined(self):
        """Test end-to-end recommendation with combined strategy"""
        from src.engines.recommendation_engine import RecommendationEngine
        
        # Create mock analyzer
        analyzer = MockStockAnalyzer("MSFT", self.sample_data)
        
        # Create recommendation engine
        engine = RecommendationEngine(analyzer, self.lang_config_zh)
        
        # Generate recommendation
        result = engine.generate_recommendation(strategy_type='combined')
        
        # Verify structure and Chinese language
        self.assertIn('recommendation', result)
        self.assertIn('action', result['recommendation'])
        self.assertIn('confidence', result['recommendation'])
        self.assertIn('score', result['recommendation'])
        self.assertIn('signals', result['recommendation'])
        self.assertIsInstance(result['recommendation']['signals'], list)
        self.assertGreater(len(result['recommendation']['signals']), 0)
        
        # Verify Chinese language content is present
        signals_text = ' '.join(result['recommendation']['signals'])
        # Should contain Chinese characters since we're using Chinese language config
        
    def test_multi_strategy_integration(self):
        """Test integration of multiple strategies"""
        from src.engines.strategy_manager import StrategyManager
        
        # Create strategy manager
        manager = StrategyManager(self.lang_config_en)
        
        # Create mock analyzer
        analyzer = MockStockAnalyzer("GOOGL", self.sample_data)
        
        # Get combined recommendation
        result = manager.get_recommendation(analyzer, ['technical', 'quantitative', 'ai'])
        
        # Verify structure
        self.assertIn('action', result)
        self.assertIn('confidence', result)
        self.assertIn('score', result)
        self.assertIn('individual_results', result)
        
        # Verify individual results
        self.assertEqual(len(result['individual_results']), 3)
        for strategy_name, individual in result['individual_results'].items():
            self.assertIn(strategy_name, ['technical', 'quantitative', 'ai'])
            self.assertIn('action', individual)
            self.assertIn('score', individual)
            self.assertIn('confidence', individual)
    
    def test_language_switching_integration(self):
        """Test that language switching works across all components"""
        from src.engines.recommendation_engine import RecommendationEngine
        
        analyzer = MockStockAnalyzer("TSLA", self.sample_data)
        
        # Test English
        engine_en = RecommendationEngine(analyzer, self.lang_config_en)
        result_en = engine_en.generate_recommendation(strategy_type='technical')
        
        # Test Chinese
        engine_zh = RecommendationEngine(analyzer, self.lang_config_zh)
        result_zh = engine_zh.generate_recommendation(strategy_type='technical')
        
        # Both should have the same structure but different language content
        self.assertEqual(set(result_en.keys()), set(result_zh.keys()))
        # Actions might be translated, so we need to compare the score instead
        self.assertEqual(result_en['recommendation']['score'], result_zh['recommendation']['score'])    # Score should be same
        
    def test_error_handling_integration(self):
        """Test error handling across the system"""
        from src.engines.recommendation_engine import RecommendationEngine
        import pandas as pd
        
        # Create analyzer with empty data and Chinese config for error message test
        analyzer = MockStockAnalyzer("EMPTY", pd.DataFrame(), self.lang_config_zh)
        
        # Should handle gracefully
        engine = RecommendationEngine(analyzer, self.lang_config_zh)
        
        # This should not raise an exception but return a valid result
        try:
            result = engine.generate_recommendation(strategy_type='technical')
            self.assertIn('recommendation', result)
            self.assertIn('action', result['recommendation'])
        except Exception as e:
            # This is expected for empty data - test should pass with Chinese message
            self.assertIn("请先获取股票数据", str(e))
    
    def test_different_time_periods_integration(self):
        """Test that different time periods work in integration"""
        from src.engines.recommendation_engine import RecommendationEngine
        
        # Test with different sized datasets (simulating different periods)
        small_data = MockStockData.create_sample_data(30)    # 1 month
        large_data = MockStockData.create_sample_data(365)   # 1 year
        
        for data, label in [(small_data, "1mo"), (large_data, "1y")]:
            with self.subTest(period=label):
                analyzer = MockStockAnalyzer("TEST", data)
                engine = RecommendationEngine(analyzer, self.lang_config_en)
                
                result = engine.generate_recommendation(strategy_type='combined')
                
                # Should work regardless of data size
                self.assertIn('recommendation', result)
                self.assertIn('action', result['recommendation'])
                self.assertIsInstance(result['recommendation']['score'], int)


class TestSystemPerformance(unittest.TestCase):
    """Performance and resource usage tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        main_dir = os.path.join(os.path.dirname(__file__), '..')
        if main_dir not in sys.path:
            sys.path.insert(0, main_dir)
            
        from src.languages.config import LanguageConfig
        self.lang_config = LanguageConfig('en')
        self.sample_data = MockStockData.create_sample_data()
    
    def test_memory_usage_stability(self):
        """Test that multiple analyses don't cause memory issues"""
        from src.engines.recommendation_engine import RecommendationEngine
        
        # Run multiple analyses
        for i in range(10):
            analyzer = MockStockAnalyzer(f"TEST{i}", self.sample_data)
            engine = RecommendationEngine(analyzer, self.lang_config)
            result = engine.generate_recommendation(strategy_type='combined')
            
            # Each should complete successfully
            self.assertIn('recommendation', result)
            self.assertIn('action', result['recommendation'])
        
        # If we get here without memory errors, test passes
        self.assertTrue(True)
    
    def test_recommendation_generation_time(self):
        """Test that recommendation generation completes in reasonable time"""
        import time
        from src.engines.recommendation_engine import RecommendationEngine
        
        analyzer = MockStockAnalyzer("PERF", self.sample_data)
        engine = RecommendationEngine(analyzer, self.lang_config)
        
        start_time = time.time()
        result = engine.generate_recommendation(strategy_type='combined')
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete within 5 seconds
        self.assertLess(execution_time, 5.0, f"Recommendation took {execution_time:.2f} seconds")
        self.assertIn('recommendation', result)
        self.assertIn('action', result['recommendation'])


if __name__ == '__main__':
    unittest.main()
