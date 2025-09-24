"""
Technical Indicator based trading strategy
"""
from typing import Dict, List
from .base_strategy import TradingStrategy


class TechnicalIndicatorStrategy(TradingStrategy):
    """Technical Indicator based trading strategy"""
    
    def analyze(self, analyzer) -> Dict:
        """Analyze using technical indicators"""
        metrics = analyzer.get_current_metrics()
        score = 0
        reasons = []
        
        # RSI Analysis (Weight: 30%)
        rsi = metrics['rsi']
        if rsi < 30:
            score += 30
            reasons.append(self._format_reason("strategy_rsi_oversold", rsi))
        elif rsi > 70:
            score -= 30
            reasons.append(self._format_reason("strategy_rsi_overbought", rsi))
        elif 40 <= rsi <= 60:
            score += 10
            reasons.append(self._format_reason("strategy_rsi_neutral", rsi))
        
        # MACD Analysis (Weight: 25%)
        macd = metrics['macd']
        macd_signal = metrics['macd_signal']
        if macd > macd_signal:
            if macd > 0:
                score += 25
                reasons.append(self._format_reason("strategy_macd_strong_bullish"))
            else:
                score += 15
                reasons.append(self._format_reason("strategy_macd_bullish"))
        else:
            if macd < 0:
                score -= 25
                reasons.append(self._format_reason("strategy_macd_strong_bearish"))
            else:
                score -= 15
                reasons.append(self._format_reason("strategy_macd_bearish"))
        
        # Moving Average Analysis (Weight: 25%)
        current_price = metrics['current_price']
        sma_20 = metrics['sma_20']
        sma_50 = metrics['sma_50']
        
        if current_price > sma_20 > sma_50:
            score += 25
            reasons.append(self._format_reason("strategy_ma_strong_uptrend"))
        elif current_price > sma_20:
            score += 15
            reasons.append(self._format_reason("strategy_ma_above_short"))
        elif current_price < sma_20 < sma_50:
            score -= 25
            reasons.append(self._format_reason("strategy_ma_strong_downtrend"))
        elif current_price < sma_20:
            score -= 15
            reasons.append(self._format_reason("strategy_ma_below_short"))
        
        # Bollinger Bands Analysis (Weight: 20%)
        bb_upper = metrics['bb_upper']
        bb_lower = metrics['bb_lower']
        bb_middle = (bb_upper + bb_lower) / 2
        
        if current_price < bb_lower:
            score += 20
            reasons.append(self._format_reason("strategy_bb_oversold"))
        elif current_price > bb_upper:
            score -= 15  # Less negative as it could be a breakout
            reasons.append(self._format_reason("strategy_bb_overbought"))
        elif current_price > bb_middle:
            score += 5
            reasons.append(self._format_reason("strategy_bb_above_middle"))
        
        return self._generate_recommendation(score, reasons, "Technical")
    
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
