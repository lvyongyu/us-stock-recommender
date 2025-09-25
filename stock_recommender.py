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
from src.batch.input_parser import InputParser


def main():
    """Main function with multi-language support and multi-stock analysis"""
    parser = argparse.ArgumentParser(description=EN_TEXTS["help_description"])
    
    # Single stock mode parameters
    parser.add_argument('symbol', nargs='?', help=f'{EN_TEXTS["help_symbol"]} / {ZH_TEXTS["help_symbol"]} {EN_TEXTS["help_single_stock_mode"]} / {ZH_TEXTS["help_single_stock_mode"]}')
    
    # Multi-stock mode parameters
    parser.add_argument('--multi', nargs='?', const='', metavar='SYMBOLS', 
                      help=f'{EN_TEXTS["help_multi_stock_mode"]} / {ZH_TEXTS["help_multi_stock_mode"]}')
    parser.add_argument('--file', metavar='FILE', help=f'{EN_TEXTS["help_file_input"]} / {ZH_TEXTS["help_file_input"]}')
    
    parser.add_argument('--period', default='1y', help=f'{EN_TEXTS["help_period"]} / {ZH_TEXTS["help_period"]}')
    parser.add_argument('--lang', default='en', choices=['en', 'zh'], 
                      help=f'{EN_TEXTS["help_language"]} / {ZH_TEXTS["help_language"]}')
    parser.add_argument('--strategy', default='combined', 
                      choices=['technical', 'quantitative', 'ai', 'combined'],
                      help='Strategy type: technical (Technical Indicator), quantitative (Quantitative Model), ai (AI/ML), combined (All strategies)')
    
    args = parser.parse_args()
    
        # Validate argument combinations
    if args.multi is not None:
        if not args.multi and not args.file:
            error_msg = "使用 --multi 时必须提供股票代码或配合 --file 参数" if args.lang == 'zh' else "When using --multi, you must provide stock symbols or use --file parameter"
            parser.error(error_msg)
        if args.symbol:
            error_msg = "多股票模式不能同时使用单股票参数" if args.lang == 'zh' else "Cannot use single stock argument with multi-stock mode"
            parser.error(error_msg)
    elif args.file:
        error_msg = "--file 参数必须与 --multi 参数配合使用" if args.lang == 'zh' else "--file parameter must be used with --multi parameter"
        parser.error(error_msg)
    elif not args.symbol:
        error_msg = "必须提供股票代码或使用多股票模式（--multi）" if args.lang == 'zh' else "Must provide stock symbol or use multi-stock mode (--multi)"
        parser.error(error_msg)
    
    # Initialize language configuration
    lang_config = LanguageConfig(args.lang)
    
    try:
        # Determine execution mode
        if args.symbol:
            # Single stock mode (original logic)
            return run_single_stock_analysis(args, lang_config)
        elif args.multi is not None:
            # Multi-stock mode (new feature)
            return run_multi_stock_analysis(args, lang_config)
        else:
            print(lang_config.get("error_must_specify_stock"))
            return 1
            
    except Exception as e:
        print(lang_config.get("error").format(str(e)))
        return 1


def run_single_stock_analysis(args, lang_config):
    """Run single stock analysis (original functionality)"""
    print(lang_config.get("analyzing").format(args.symbol))
    
    # Create analyzer and recommendation engine
    analyzer = StockAnalyzer(args.symbol, lang_config)
    analyzer.fetch_data(args.period)  # 设置数据周期
    engine = RecommendationEngine(analyzer, lang_config)
    
    # Generate recommendation
    recommendation = engine.generate_recommendation(strategy_type=args.strategy)
    
    # Output report with selected language
    print(format_recommendation_report(recommendation, lang_config))
    
    return 0


def display_batch_recommendations(result, lang_config):
    """Display batch recommendation results"""
    if not result.successful_analyses:
        print(lang_config.get("no_successful_analysis"))
        return
    
    print(f"\n" + "="*80)
    print(lang_config.get("stock_recommendation_results"))
    print("="*80)
    
    # Categorize by recommendation action
    buy_stocks = []
    sell_stocks = []
    hold_stocks = []
    short_stocks = []
    
    for analysis in result.successful_analyses:
        symbol = analysis['symbol']
        recommendation = analysis['recommendation']
        action = recommendation['action']
        score = recommendation.get('score', 0)
        confidence = recommendation.get('confidence', 'Medium')
        
        stock_info = {
            'symbol': symbol,
            'score': score,
            'confidence': confidence,
            'analysis': analysis
        }
        
        if action == 'Buy':
            buy_stocks.append(stock_info)
        elif action == 'Sell':
            sell_stocks.append(stock_info)
        elif action == 'Short':
            short_stocks.append(stock_info)
        else:  # Hold
            hold_stocks.append(stock_info)
    
    # Sort by score
    buy_stocks.sort(key=lambda x: x['score'], reverse=True)
    sell_stocks.sort(key=lambda x: x['score'])
    short_stocks.sort(key=lambda x: x['score'])
    hold_stocks.sort(key=lambda x: x['score'], reverse=True)
    
    # Display buy recommendations
    if buy_stocks:
        print(f"\n{lang_config.get('buy_recommendations').format(len(buy_stocks))}")
        for stock in buy_stocks:
            print(f"   📈 {lang_config.get('stock_score_confidence').format(stock['symbol'], stock['score'], stock['confidence'])}")
    
    # Display sell recommendations
    if sell_stocks:
        print(f"\n{lang_config.get('sell_recommendations').format(len(sell_stocks))}")
        for stock in sell_stocks:
            print(f"   📉 {lang_config.get('stock_score_confidence').format(stock['symbol'], stock['score'], stock['confidence'])}")
    
    # Display short recommendations
    if short_stocks:
        print(f"\n{lang_config.get('short_recommendations').format(len(short_stocks))}")
        for stock in short_stocks:
            print(f"   📉 {lang_config.get('stock_score_confidence').format(stock['symbol'], stock['score'], stock['confidence'])}")
    
    # Display hold recommendations
    if hold_stocks:
        print(f"\n{lang_config.get('hold_recommendations').format(len(hold_stocks))}")
        for stock in hold_stocks:
            print(f"   ⏸️  {lang_config.get('stock_score_confidence').format(stock['symbol'], stock['score'], stock['confidence'])}")
    
    # Display portfolio suggestions
    print(f"\n{lang_config.get('portfolio_title')}")
    if buy_stocks:
        top_buys = buy_stocks[:min(5, len(buy_stocks))]
        print(f"   {lang_config.get('portfolio_top_picks').format(len(top_buys), ', '.join([s['symbol'] for s in top_buys]))}")
    
    if sell_stocks or short_stocks:
        risk_stocks = (sell_stocks + short_stocks)[:5]
        print(f"   {lang_config.get('risk_stocks').format(', '.join([s['symbol'] for s in risk_stocks]))}")
    
    print("="*80)


def run_multi_stock_analysis(args, lang_config):
    """Run multi-stock analysis"""
    from src.batch.input_parser import InputParser
    from src.batch.batch_analyzer import BatchAnalyzer
    
    try:
        # Parse input
        input_parser = InputParser(lang_config)
        if args.multi:  # Command line stock symbols provided
            parse_result = input_parser.parse_input(symbols=args.multi)
        elif args.file:  # Use file input
            parse_result = input_parser.parse_input(file_path=args.file)
        else:
            print(lang_config.get("no_valid_stock_input"))
            return 1
        
        # Check parsing results
        if parse_result['errors']:
            print(lang_config.get("input_parsing_warnings"))
            for error in parse_result['errors']:
                print(f"   • {error}")
        
        stock_symbols = parse_result['symbols']
        if not stock_symbols:
            print(lang_config.get("no_valid_stock_symbols"))
            return 1
        
        print(lang_config.get("parsing_summary").format(parse_result['valid_count'], parse_result['original_count']))
        
        # Create batch analyzer
        batch_analyzer = BatchAnalyzer(lang_config, period=args.period)
        
        # Execute batch analysis
        result = batch_analyzer.analyze_stocks(
            symbols=stock_symbols,
            strategy_type=args.strategy,
            show_progress=True
        )
        
        # Display recommendation results
        display_batch_recommendations(result, lang_config)
        
        return 0
        
    except Exception as e:
        print(lang_config.get("multi_stock_analysis_failed").format(str(e)))
        return 1


if __name__ == "__main__":
    exit(main())
