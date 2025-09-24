#!/usr/bin/env python3
"""
US Stock Recommendation System
A multi-strategy stock analysis and recommendation tool with multi-language support.

Author: Eric
License: MIT
"""

import argparse
import sys
import os

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.languages.config import LanguageConfig
from src.languages.en import TEXTS as EN_TEXTS
from src.languages.zh import TEXTS as ZH_TEXTS
from src.analyzers.stock_analyzer import StockAnalyzer
from src.engines.recommendation_engine import RecommendationEngine
from src.utils.formatters import format_recommendation_report


def main():
    """Main function with multi-language support"""
    parser = argparse.ArgumentParser(description=EN_TEXTS["help_description"])
    parser.add_argument('symbol', help=f'{EN_TEXTS["help_symbol"]} / {ZH_TEXTS["help_symbol"]}')
    parser.add_argument('--period', default='1y', help=f'{EN_TEXTS["help_period"]} / {ZH_TEXTS["help_period"]}')
    parser.add_argument('--lang', default='en', choices=['en', 'zh'], 
                      help=f'{EN_TEXTS["help_language"]} / {ZH_TEXTS["help_language"]}')
    parser.add_argument('--strategy', default='combined', 
                      choices=['technical', 'quantitative', 'ai', 'combined'],
                      help='Strategy type: technical (Technical Indicator), quantitative (Quantitative Model), ai (AI/ML), combined (All strategies)')
    
    args = parser.parse_args()
    
    # Initialize language configuration
    lang_config = LanguageConfig(args.lang)
    
    try:
        print(lang_config.get("analyzing").format(args.symbol))
        
        # Create analyzer and recommendation engine
        analyzer = StockAnalyzer(args.symbol, lang_config)
        analyzer.fetch_data(args.period)  # 设置数据周期
        engine = RecommendationEngine(analyzer, lang_config)
        
        # Generate recommendation
        recommendation = engine.generate_recommendation(strategy_type=args.strategy)
        
        # Output report with selected language
        print(format_recommendation_report(recommendation, lang_config))
        
    except Exception as e:
        print(lang_config.get("error").format(str(e)))
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
