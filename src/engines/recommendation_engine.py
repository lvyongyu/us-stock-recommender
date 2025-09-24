"""
Recommendation engine for generating stock investment recommendations
"""
from datetime import datetime
from typing import Dict, List
from ..engines.strategy_manager import StrategyManager


class RecommendationEngine:
    """Enhanced recommendation engine with multiple trading strategies"""
    
    def __init__(self, analyzer, lang_config, strategies: List[str] = None):
        self.analyzer = analyzer
        self.lang_config = lang_config
        self.strategy_manager = StrategyManager(lang_config)
        self.strategies = strategies or ['all']
    
    def generate_recommendation(self, strategy_type: str = 'combined') -> Dict:
        """Generate enhanced investment recommendation using selected strategies"""
        try:
            # Convert strategy_type to strategy list
            if strategy_type == 'combined':
                strategies = ['all']
            else:
                strategies = [strategy_type]
            
            # Get strategy-based recommendation
            recommendation = self.strategy_manager.get_recommendation(
                self.analyzer, 
                strategies
            )
            
            # Get basic metrics for display
            metrics = self.analyzer.get_current_metrics()
            
            # Analyze trend, momentum, volume for display (legacy support)
            trend = self._analyze_trend(metrics)
            momentum = self._analyze_momentum(metrics)
            volume = self._analyze_volume(metrics)
            
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
                'recommendation': {
                    'action': self.lang_config.get(recommendation['action']),
                    'confidence': self._format_confidence(recommendation['confidence']),
                    'score': recommendation['score'],
                    'signals': recommendation['reasons']
                },
                'risk_level': risk_level,
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'strategy_used': recommendation.get('strategy_name', recommendation['strategy']),
                'key_metrics': {
                    'RSI': round(metrics['rsi'], 2),
                    'MACD': round(metrics['macd'], 4),
                    'SMA20': round(metrics['sma_20'], 2),
                    'SMA50': round(metrics['sma_50'], 2),
                }
            }
            
            # Add individual strategy results if available
            if 'individual_results' in recommendation:
                result['individual_strategies'] = recommendation['individual_results']
            
            return result
            
        except Exception as e:
            raise Exception(f"Recommendation generation failed: {str(e)}")
    
    def _analyze_trend(self, metrics: Dict) -> str:
        """Legacy trend analysis for display"""
        current_price = metrics['current_price']
        sma_20 = metrics['sma_20']
        sma_50 = metrics['sma_50']
        
        if current_price > sma_20 > sma_50:
            return self.lang_config.get("uptrend")
        elif current_price < sma_20 < sma_50:
            return self.lang_config.get("downtrend")
        else:
            return self.lang_config.get("sideways")
    
    def _analyze_momentum(self, metrics: Dict) -> str:
        """Legacy momentum analysis for display"""
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
    
    def _analyze_volume(self, metrics: Dict) -> str:
        """Legacy volume analysis for display"""
        current_volume = metrics['volume']
        avg_volume = metrics['avg_volume']
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 1.5:
            return self.lang_config.get("volume_high")
        elif volume_ratio < 0.5:
            return self.lang_config.get("volume_low")
        else:
            return self.lang_config.get("volume_normal")
    
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
    
    def _format_confidence(self, confidence: float) -> str:
        """Format confidence level"""
        if confidence >= 0.7:
            return self.lang_config.get("high")
        elif confidence >= 0.4:
            return self.lang_config.get("medium")
        else:
            return self.lang_config.get("low")
