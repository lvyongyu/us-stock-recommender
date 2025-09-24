"""
Utility functions for formatting reports and other helper functions
"""
from typing import Dict


def format_recommendation_report(recommendation: Dict, lang_config) -> str:
    """Format recommendation report based on selected language"""
    
    separator = '='*60
    
    report = f"""
{separator}
           {lang_config.get('report_title')}
{separator}

{lang_config.get('stock_code')}: {recommendation['symbol']}
{lang_config.get('current_price')}: ${recommendation['current_price']:.2f}
{lang_config.get('price_change')}: ${recommendation['price_change']:+.2f} ({recommendation['price_change_pct']:+.2f}%)
{lang_config.get('analysis_time')}: {recommendation['analysis_time']}

{separator}
{lang_config.get('technical_analysis')}
{separator}
{lang_config.get('trend_analysis')}: {recommendation['trend']}
{lang_config.get('momentum_indicators')}: {recommendation['momentum']}
{lang_config.get('volume_analysis')}: {recommendation['volume']}

{lang_config.get('key_metrics')}:
- RSI: {recommendation['key_metrics']['RSI']}
- MACD: {recommendation['key_metrics']['MACD']:.4f}
- {lang_config.get('key_metrics').split(':')[0] if ':' in lang_config.get('key_metrics') else 'SMA'} 20: ${recommendation['key_metrics']['SMA20']:.2f}
- {lang_config.get('key_metrics').split(':')[0] if ':' in lang_config.get('key_metrics') else 'SMA'} 50: ${recommendation['key_metrics']['SMA50']:.2f}

{separator}
{lang_config.get('investment_advice')}
{separator}
{lang_config.get('recommended_action')}: {recommendation['recommendation']['action']}
{lang_config.get('confidence_level')}: {recommendation['recommendation']['confidence']}
{lang_config.get('risk_rating')}: {recommendation['risk_level']}
{lang_config.get('composite_score')}: {recommendation['recommendation']['score']}/100

{lang_config.get('analysis_basis')}:
"""
    
    for i, signal in enumerate(recommendation['recommendation']['signals'], 1):
        report += f"{i}. {signal}\n"
    
    report += f"\n{separator}\n"
    report += f"{lang_config.get('disclaimer')}\n"
    report += separator
    
    return report
