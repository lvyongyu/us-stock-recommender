#!/usr/bin/env python3
"""
US Stock Recommendation System
输入股票代码，生成投资策略推荐（买入、卖出、做空等）
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse


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
    """推荐引擎 - 基于技术分析生成投资策略"""
    
    def __init__(self, analyzer: StockAnalyzer):
        self.analyzer = analyzer
    
    def analyze_trend(self, metrics: Dict) -> str:
        """分析趋势方向"""
        current_price = metrics['current_price']
        sma_20 = metrics['sma_20']
        sma_50 = metrics['sma_50']
        
        if current_price > sma_20 > sma_50:
            return "上升趋势"
        elif current_price < sma_20 < sma_50:
            return "下降趋势"
        else:
            return "震荡趋势"
    
    def analyze_momentum(self, metrics: Dict) -> str:
        """分析动量指标"""
        rsi = metrics['rsi']
        macd = metrics['macd']
        macd_signal = metrics['macd_signal']
        
        momentum_signals = []
        
        if rsi > 70:
            momentum_signals.append("RSI超买")
        elif rsi < 30:
            momentum_signals.append("RSI超卖")
        else:
            momentum_signals.append("RSI中性")
            
        if macd > macd_signal:
            momentum_signals.append("MACD看涨")
        else:
            momentum_signals.append("MACD看跌")
        
        return " | ".join(momentum_signals)
    
    def analyze_volume(self, metrics: Dict) -> str:
        """分析成交量"""
        current_volume = metrics['volume']
        avg_volume = metrics['avg_volume']
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 1.5:
            return "成交量放大"
        elif volume_ratio < 0.5:
            return "成交量萎缩"
        else:
            return "成交量正常"
    
    def generate_recommendation(self) -> Dict:
        """生成投资建议"""
        try:
            self.analyzer.fetch_data()
            metrics = self.analyzer.get_current_metrics()
            
            # 分析各个方面
            trend = self.analyze_trend(metrics)
            momentum = self.analyze_momentum(metrics)
            volume = self.analyze_volume(metrics)
            
            # 生成推荐策略
            recommendation = self._calculate_recommendation(metrics)
            
            # 计算风险等级
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
        """计算推荐策略"""
        score = 0
        signals = []
        
        # 趋势分析 (权重: 30%)
        if metrics['current_price'] > metrics['sma_20']:
            score += 15
            signals.append("价格在20日均线上方")
        else:
            score -= 15
            signals.append("价格在20日均线下方")
            
        if metrics['sma_20'] > metrics['sma_50']:
            score += 15
            signals.append("短期均线上穿长期均线")
        else:
            score -= 15
            signals.append("短期均线下穿长期均线")
        
        # RSI分析 (权重: 25%)
        rsi = metrics['rsi']
        if rsi < 30:
            score += 25
            signals.append("RSI超卖，可能反弹")
        elif rsi > 70:
            score -= 25
            signals.append("RSI超买，可能回调")
        elif 40 <= rsi <= 60:
            score += 10
            signals.append("RSI中性区域")
        
        # MACD分析 (权重: 25%)
        if metrics['macd'] > metrics['macd_signal']:
            score += 25
            signals.append("MACD金叉看涨")
        else:
            score -= 25
            signals.append("MACD死叉看跌")
        
        # 布林带分析 (权重: 20%)
        current_price = metrics['current_price']
        if current_price < metrics['bb_lower']:
            score += 20
            signals.append("价格触及布林带下轨")
        elif current_price > metrics['bb_upper']:
            score -= 20
            signals.append("价格触及布林带上轨")
        
        # 生成最终推荐
        if score >= 50:
            action = "强烈买入"
            confidence = "高"
        elif score >= 25:
            action = "买入"
            confidence = "中等"
        elif score >= -25:
            action = "持有"
            confidence = "中等"
        elif score >= -50:
            action = "卖出"
            confidence = "中等"
        else:
            action = "强烈卖出/做空"
            confidence = "高"
        
        return {
            'action': action,
            'confidence': confidence,
            'score': score,
            'signals': signals
        }
    
    def _assess_risk(self, metrics: Dict) -> str:
        """评估风险等级"""
        risk_factors = 0
        
        # 波动性风险
        if metrics['rsi'] > 80 or metrics['rsi'] < 20:
            risk_factors += 1
        
        # 成交量异常
        volume_ratio = metrics['volume'] / metrics['avg_volume']
        if volume_ratio > 2 or volume_ratio < 0.3:
            risk_factors += 1
        
        # 价格变动幅度
        if abs(metrics['price_change_pct']) > 5:
            risk_factors += 1
        
        if risk_factors >= 2:
            return "高风险"
        elif risk_factors == 1:
            return "中等风险"
        else:
            return "低风险"


def format_recommendation_report(recommendation: Dict) -> str:
    """格式化推荐报告"""
    report = f"""
{'='*60}
           美股投资策略推荐报告
{'='*60}

股票代码: {recommendation['symbol']}
当前价格: ${recommendation['current_price']:.2f}
价格变动: ${recommendation['price_change']:+.2f} ({recommendation['price_change_pct']:+.2f}%)
分析时间: {recommendation['analysis_time']}

{'='*60}
技术分析
{'='*60}
趋势分析: {recommendation['trend']}
动量指标: {recommendation['momentum']}
成交量分析: {recommendation['volume']}

关键技术指标:
- RSI: {recommendation['key_metrics']['RSI']}
- MACD: {recommendation['key_metrics']['MACD']:.4f}
- 20日均线: ${recommendation['key_metrics']['SMA20']:.2f}
- 50日均线: ${recommendation['key_metrics']['SMA50']:.2f}

{'='*60}
投资建议
{'='*60}
推荐操作: {recommendation['recommendation']['action']}
信心等级: {recommendation['recommendation']['confidence']}
风险评级: {recommendation['risk_level']}
综合评分: {recommendation['recommendation']['score']}/100

分析依据:
"""
    
    for i, signal in enumerate(recommendation['recommendation']['signals'], 1):
        report += f"{i}. {signal}\n"
    
    report += f"\n{'='*60}\n"
    report += "免责声明: 本分析仅供参考，投资有风险，决策需谨慎！\n"
    report += "='*60"
    
    return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='美股推荐系统')
    parser.add_argument('symbol', help='股票代码 (例如: AAPL, TSLA, MSFT)')
    parser.add_argument('--period', default='1y', help='数据时间范围 (默认: 1y)')
    
    args = parser.parse_args()
    
    try:
        print(f"正在分析股票: {args.symbol}...")
        
        # 创建分析器和推荐引擎
        analyzer = StockAnalyzer(args.symbol)
        engine = RecommendationEngine(analyzer)
        
        # 生成推荐
        recommendation = engine.generate_recommendation()
        
        # 输出报告
        print(format_recommendation_report(recommendation))
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
