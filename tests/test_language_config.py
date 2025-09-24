"""
Unit tests for language configuration
"""
import unittest
from tests.test_utils import TestConfig
from src.languages.config import LanguageConfig


class TestLanguageConfig(unittest.TestCase):
    """Test language configuration functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.en_config = LanguageConfig('en')
        self.zh_config = LanguageConfig('zh')
    
    def test_language_initialization(self):
        """Test language config initialization"""
        # Test English (default)
        config_en = LanguageConfig('en')
        self.assertEqual(config_en.language, 'en')
        
        # Test Chinese
        config_zh = LanguageConfig('zh')
        self.assertEqual(config_zh.language, 'zh')
        
        # Test default language
        config_default = LanguageConfig()
        self.assertEqual(config_default.language, 'en')
    
    def test_language_text_loading(self):
        """Test that texts are loaded correctly"""
        # Test that we get different texts for different languages
        en_analyzing = self.en_config.get('analyzing')
        zh_analyzing = self.zh_config.get('analyzing')
        
        self.assertNotEqual(en_analyzing, zh_analyzing)
        self.assertIn('{}', en_analyzing)  # Should have placeholder
        self.assertIn('{}', zh_analyzing)  # Should have placeholder
    
    def test_common_keys_exist(self):
        """Test that common keys exist in both languages"""
        common_keys = [
            'analyzing', 'error', 'report_title', 'stock_code',
            'current_price', 'price_change', 'analysis_time',
            'technical_analysis', 'investment_advice', 'disclaimer',
            'buy', 'sell', 'hold', 'strong_buy', 'strong_sell',
            'high', 'medium', 'low', 'uptrend', 'downtrend', 'sideways'
        ]
        
        for key in common_keys:
            with self.subTest(key=key):
                en_text = self.en_config.get(key)
                zh_text = self.zh_config.get(key)
                
                # Both should return non-empty strings
                self.assertIsInstance(en_text, str)
                self.assertIsInstance(zh_text, str)
                self.assertNotEqual(en_text, key)  # Should not return key itself
                self.assertNotEqual(zh_text, key)  # Should not return key itself
    
    def test_missing_key_handling(self):
        """Test handling of missing keys"""
        missing_key = 'non_existent_key_12345'
        result = self.en_config.get(missing_key)
        self.assertEqual(result, missing_key)  # Should return key itself
    
    def test_strategy_specific_keys(self):
        """Test strategy-specific language keys"""
        strategy_keys = [
            'strategy_technical', 'strategy_quantitative', 'strategy_ai',
            'strategy_combined', 'strategy_rsi_oversold', 'strategy_rsi_overbought',
            'strategy_macd_bullish', 'strategy_macd_bearish'
        ]
        
        for key in strategy_keys:
            with self.subTest(key=key):
                en_text = self.en_config.get(key)
                zh_text = self.zh_config.get(key)
                
                # Should get different translations
                self.assertNotEqual(en_text, zh_text)
    
    def test_case_insensitive_language(self):
        """Test case insensitive language selection"""
        configs = [
            LanguageConfig('EN'),
            LanguageConfig('En'),
            LanguageConfig('eN'),
            LanguageConfig('ZH'),
            LanguageConfig('Zh'),
            LanguageConfig('zH')
        ]
        
        en_configs = configs[:3]
        zh_configs = configs[3:]
        
        # All EN configs should behave the same
        base_en_text = self.en_config.get('analyzing')
        for config in en_configs:
            self.assertEqual(config.get('analyzing'), base_en_text)
        
        # All ZH configs should behave the same
        base_zh_text = self.zh_config.get('analyzing')
        for config in zh_configs:
            self.assertEqual(config.get('analyzing'), base_zh_text)


if __name__ == '__main__':
    unittest.main()
