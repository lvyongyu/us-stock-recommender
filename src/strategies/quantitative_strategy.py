"""
Quantitative model based trading strategy
"""
from typing import Dict, List
from .base_strategy import TradingStrategy


class QuantitativeStrategy(TradingStrategy):
    """Quantitative model based trading strategy"""
    
    def analyze(self, analyzer) -> Dict:
        """Analyze using quantitative models"""
        metrics = analyzer.get_current_metrics()
        data = analyzer.data
        score = 0
        reasons = []
        
        # Price momentum (Weight: 25%)
        returns_5d = data['Close'].pct_change(5).iloc[-1] * 100
        returns_20d = data['Close'].pct_change(20).iloc[-1] * 100
        
        if returns_5d > 2 and returns_20d > 5:
            score += 25
            reasons.append(self._format_reason("strategy_momentum_strong", returns_5d, returns_20d))
        elif returns_5d > 0 and returns_20d > 0:
            score += 15
            reasons.append(self._format_reason("strategy_momentum_positive", returns_5d, returns_20d))
        elif returns_5d < -2 and returns_20d < -5:
            score -= 25
            reasons.append(self._format_reason("strategy_momentum_weak", returns_5d, returns_20d))
        elif returns_5d < 0 and returns_20d < 0:
            score -= 15
            reasons.append(self._format_reason("strategy_momentum_negative", returns_5d, returns_20d))
        
        # Volatility analysis (Weight: 20%)
        volatility_20d = data['Close'].rolling(20).std().iloc[-1] / data['Close'].iloc[-1] * 100
        avg_volatility = data['Close'].rolling(60).std().mean() / data['Close'].mean() * 100
        
        if volatility_20d < avg_volatility * 0.8:
            score += 15
            reasons.append(self._format_reason("strategy_volatility_low"))
        elif volatility_20d > avg_volatility * 1.5:
            score -= 10
            reasons.append(self._format_reason("strategy_volatility_high"))
        
        # Volume analysis (Weight: 20%)
        avg_volume_20 = data['Volume'].rolling(20).mean().iloc[-1]
        current_volume = metrics['volume']
        volume_ratio = current_volume / avg_volume_20
        
        if volume_ratio > 1.5 and returns_5d > 0:
            score += 20
            reasons.append(self._format_reason("strategy_volume_surge_bullish", volume_ratio))
        elif volume_ratio > 1.5 and returns_5d < 0:
            score -= 20
            reasons.append(self._format_reason("strategy_volume_surge_bearish", volume_ratio))
        elif volume_ratio < 0.5:
            score -= 10
            reasons.append(self._format_reason("strategy_volume_low"))
        
        # Mean reversion potential (Weight: 35%)
        current_price = metrics['current_price']
        sma_50 = metrics['sma_50']
        deviation = (current_price - sma_50) / sma_50 * 100
        
        if deviation < -10:
            score += 25
            reasons.append(self._format_reason("strategy_mean_reversion_oversold", abs(deviation)))
        elif deviation > 10:
            score -= 20
            reasons.append(self._format_reason("strategy_mean_reversion_overbought", deviation))
        elif abs(deviation) < 3:
            score += 10
            reasons.append(self._format_reason("strategy_mean_reversion_fair"))
        
        return self._generate_recommendation(score, reasons, "Quantitative")
    
    def _format_reason(self, key: str, *args) -> str:
        """Format reason using language configuration"""
        return self.lang_config.get(key).format(*args) if args else self.lang_config.get(key)
    
    def _generate_recommendation(self, score: int, reasons: List[str], strategy_name: str) -> Dict:
        """Generate final recommendation based on score"""
        # Normalize score to -100 to 100
        score = max(-100, min(100, score))
        
        # Determine action and confidence
        if score >= 60:
            action = "strong_buy"
            confidence = min(0.9, 0.6 + (score - 60) * 0.01)
        elif score >= 25:
            action = "buy" 
            confidence = 0.5 + (score - 25) * 0.01
        elif score >= -25:
            action = "hold"
            confidence = 0.3 + abs(score) * 0.005
        elif score >= -60:
            action = "sell"
            confidence = 0.5 + (abs(score) - 25) * 0.01
        else:
            action = "strong_sell"
            confidence = min(0.9, 0.6 + (abs(score) - 60) * 0.01)
        
        return {
            'action': action,
            'confidence': round(confidence, 2),
            'score': score,
            'reasons': reasons,
            'strategy': strategy_name
        }
