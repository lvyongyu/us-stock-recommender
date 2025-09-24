#!/usr/bin/env python3
"""
US Stock Recommendation System
Multi-language support: English (default) and Chinese
输入股票代码，生成投资策略推荐（买入、卖出、做空等）
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse

# Import language resources
from languages import EN_TEXTS, ZH_TEXTS


class LanguageConfig:
    """Multi-language configuration for the stock recommendation system"""
    
    def __init__(self, language: str = "en"):
        self.language = language.lower()
        self.texts = self._load_texts()
    
    def _load_texts(self) -> Dict:
        """Load text translations from resource files"""
        return ZH_TEXTS if self.language == "zh" else EN_TEXTS
    
    def get(self, key: str) -> str:
        """Get translated text by key"""
        return self.texts.get(key, key)


class StockAnalyzer:
    """股票分析器 - 负责获取和分析股票数据"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.ticker = yf.Ticker(self.symbol)
        self.data = None
        
    def fetch_data(self, period: str = "1y") -> pd.DataFrame:
        """获取股票历史数据"""
        try:
            self.data = self.ticker.history(period=period)
            if self.data.empty:
                raise ValueError(f"无法获取股票 {self.symbol} 的数据")
            return self.data
        except Exception as e:
            raise Exception(f"获取数据失败: {str(e)}")
    
    def calculate_technical_indicators(self) -> Dict:
        """计算技术指标"""
        if self.data is None or self.data.empty:
            raise ValueError("请先获取股票数据")
            
        indicators = {}
        
        # 移动平均线
        indicators['sma_20'] = self.data['Close'].rolling(window=20).mean()
        indicators['sma_50'] = self.data['Close'].rolling(window=50).mean()
        indicators['ema_12'] = self.data['Close'].ewm(span=12).mean()
        indicators['ema_26'] = self.data['Close'].ewm(span=26).mean()
        
        # MACD
        indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
        indicators['signal'] = indicators['macd'].ewm(span=9).mean()
        indicators['histogram'] = indicators['macd'] - indicators['signal']
        
        # RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        sma_20 = indicators['sma_20']
        std_20 = self.data['Close'].rolling(window=20).std()
        indicators['bb_upper'] = sma_20 + (std_20 * 2)
        indicators['bb_lower'] = sma_20 - (std_20 * 2)
        
        # 成交量分析
        indicators['volume_sma'] = self.data['Volume'].rolling(window=20).mean()
        
        return indicators
    
    def get_current_metrics(self) -> Dict:
        """获取当前股票的关键指标"""
        if self.data is None or self.data.empty:
            raise ValueError("请先获取股票数据")
            
        current_price = self.data['Close'].iloc[-1]
        indicators = self.calculate_technical_indicators()
        
        metrics = {
            'current_price': current_price,
            'previous_close': self.data['Close'].iloc[-2],
            'volume': self.data['Volume'].iloc[-1],
            'avg_volume': indicators['volume_sma'].iloc[-1],
            'sma_20': indicators['sma_20'].iloc[-1],
            'sma_50': indicators['sma_50'].iloc[-1],
            'rsi': indicators['rsi'].iloc[-1],
            'macd': indicators['macd'].iloc[-1],
            'macd_signal': indicators['signal'].iloc[-1],
            'bb_upper': indicators['bb_upper'].iloc[-1],
            'bb_lower': indicators['bb_lower'].iloc[-1],
        }
        
        # 计算价格变化
        metrics['price_change'] = current_price - metrics['previous_close']
        metrics['price_change_pct'] = (metrics['price_change'] / metrics['previous_close']) * 100
        
        return metrics


class RecommendationEngine:
    """Investment recommendation engine based on technical analysis"""
    
    def __init__(self, analyzer: StockAnalyzer, lang_config: LanguageConfig):
        self.analyzer = analyzer
        self.lang_config = lang_config
    
    def analyze_trend(self, metrics: Dict) -> str:
        """Analyze trend direction"""
        current_price = metrics['current_price']
        sma_20 = metrics['sma_20']
        sma_50 = metrics['sma_50']
        
        if current_price > sma_20 > sma_50:
            return self.lang_config.get("uptrend")
        elif current_price < sma_20 < sma_50:
            return self.lang_config.get("downtrend")
        else:
            return self.lang_config.get("sideways")
    
    def analyze_momentum(self, metrics: Dict) -> str:
        """Analyze momentum indicators"""
        rsi = metrics['rsi']
        macd = metrics['macd']
        macd_signal = metrics['macd_signal']
        
        momentum_signals = []
        
        if rsi > 70:
            momentum_signals.append(self.lang_config.get("rsi_overbought"))
        elif rsi < 30:
            momentum_signals.append(self.lang_config.get("rsi_oversold"))
        else:
            momentum_signals.append(self.lang_config.get("rsi_neutral"))
            
        if macd > macd_signal:
            momentum_signals.append(self.lang_config.get("macd_bullish"))
        else:
            momentum_signals.append(self.lang_config.get("macd_bearish"))
        
        return " | ".join(momentum_signals)
    
    def analyze_volume(self, metrics: Dict) -> str:
        """Analyze volume"""
        current_volume = metrics['volume']
        avg_volume = metrics['avg_volume']
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 1.5:
            return self.lang_config.get("volume_high")
        elif volume_ratio < 0.5:
            return self.lang_config.get("volume_low")
        else:
            return self.lang_config.get("volume_normal")
    
    def generate_recommendation(self) -> Dict:
        """Generate investment recommendation"""
        try:
            self.analyzer.fetch_data()
            metrics = self.analyzer.get_current_metrics()
            
            # Analyze different aspects
            trend = self.analyze_trend(metrics)
            momentum = self.analyze_momentum(metrics)
            volume = self.analyze_volume(metrics)
            
            # Generate recommendation strategy
            recommendation = self._calculate_recommendation(metrics)
            
            # Calculate risk level
            risk_level = self._assess_risk(metrics)
            
            result = {
                'symbol': self.analyzer.symbol,
                'current_price': metrics['current_price'],
                'price_change': metrics['price_change'],
                'price_change_pct': metrics['price_change_pct'],
                'trend': trend,
                'momentum': momentum,
                'volume': volume,
                'recommendation': recommendation,
                'risk_level': risk_level,
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'key_metrics': {
                    'RSI': round(metrics['rsi'], 2),
                    'MACD': round(metrics['macd'], 4),
                    'SMA20': round(metrics['sma_20'], 2),
                    'SMA50': round(metrics['sma_50'], 2),
                }
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"生成推荐失败: {str(e)}")
    
    def _calculate_recommendation(self, metrics: Dict) -> Dict:
        """Calculate recommendation strategy"""
        score = 0
        signals = []
        
        # Price vs SMA analysis (weight: 30%)
        current_price = metrics['current_price']
        if current_price > metrics['sma_20']:
            score += 30
            signals.append(self.lang_config.get("price_above_sma20"))
        else:
            score -= 30
            signals.append(self.lang_config.get("price_below_sma20"))
        
        # SMA crossover analysis (weight: 15%)
        if metrics['sma_20'] > metrics['sma_50']:
            score += 15
            signals.append(self.lang_config.get("sma_golden_cross"))
        else:
            score -= 15
            signals.append(self.lang_config.get("sma_death_cross"))
        
        # RSI analysis (weight: 25%)
        rsi = metrics['rsi']
        if rsi < 30:
            score += 25
            signals.append(self.lang_config.get("rsi_oversold_signal"))
        elif rsi > 70:
            score -= 25
            signals.append(self.lang_config.get("rsi_overbought_signal"))
        elif 40 <= rsi <= 60:
            score += 10
            signals.append(self.lang_config.get("rsi_neutral_zone"))
        
        # MACD analysis (weight: 25%)
        if metrics['macd'] > metrics['macd_signal']:
            score += 25
            signals.append(self.lang_config.get("macd_golden_cross"))
        else:
            score -= 25
            signals.append(self.lang_config.get("macd_death_cross"))
        
        # Bollinger Bands analysis (weight: 20%)
        current_price = metrics['current_price']
        if current_price < metrics['bb_lower']:
            score += 20
            signals.append(self.lang_config.get("bollinger_lower"))
        elif current_price > metrics['bb_upper']:
            score -= 20
            signals.append(self.lang_config.get("bollinger_upper"))
        
        # Generate final recommendation
        if score >= 50:
            action = self.lang_config.get("strong_buy")
            confidence = self.lang_config.get("high")
        elif score >= 25:
            action = self.lang_config.get("buy")
            confidence = self.lang_config.get("medium")
        elif score >= -25:
            action = self.lang_config.get("hold")
            confidence = self.lang_config.get("medium")
        elif score >= -50:
            action = self.lang_config.get("sell")
            confidence = self.lang_config.get("medium")
        else:
            action = self.lang_config.get("strong_sell")
            confidence = self.lang_config.get("high")
        
        return {
            'action': action,
            'confidence': confidence,
            'score': score,
            'signals': signals
        }
    
    def _assess_risk(self, metrics: Dict) -> str:
        """Assess risk level"""
        risk_factors = 0
        
        # Volatility risk
        if metrics['rsi'] > 80 or metrics['rsi'] < 20:
            risk_factors += 1
        
        # Volume anomaly
        volume_ratio = metrics['volume'] / metrics['avg_volume']
        if volume_ratio > 2 or volume_ratio < 0.3:
            risk_factors += 1
        
        # Price movement range
        if abs(metrics['price_change_pct']) > 5:
            risk_factors += 1
        
        if risk_factors >= 2:
            return self.lang_config.get("high_risk")
        elif risk_factors == 1:
            return self.lang_config.get("medium_risk")
        else:
            return self.lang_config.get("low_risk")


def format_recommendation_report(recommendation: Dict, lang_config: LanguageConfig) -> str:
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


def main():
    """Main function with multi-language support"""
    parser = argparse.ArgumentParser(description=EN_TEXTS["help_description"])
    parser.add_argument('symbol', help=f'{EN_TEXTS["help_symbol"]} / {ZH_TEXTS["help_symbol"]}')
    parser.add_argument('--period', default='1y', help=f'{EN_TEXTS["help_period"]} / {ZH_TEXTS["help_period"]}')
    parser.add_argument('--lang', default='en', choices=['en', 'zh'], 
                      help=f'{EN_TEXTS["help_language"]} / {ZH_TEXTS["help_language"]}')
    
    args = parser.parse_args()
    
    # Initialize language configuration
    lang_config = LanguageConfig(args.lang)
    
    try:
        print(lang_config.get("analyzing").format(args.symbol))
        
        # Create analyzer and recommendation engine
        analyzer = StockAnalyzer(args.symbol)
        engine = RecommendationEngine(analyzer, lang_config)
        
        # Generate recommendation
        recommendation = engine.generate_recommendation()
        
        # Output report with selected language
        print(format_recommendation_report(recommendation, lang_config))
        
    except Exception as e:
        print(lang_config.get("error").format(str(e)))
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
