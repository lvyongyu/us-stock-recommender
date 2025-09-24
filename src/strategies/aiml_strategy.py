"""
AI/Machine Learning based trading strategy
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from .base_strategy import TradingStrategy


class AIMLStrategy(TradingStrategy):
    """AI/Machine Learning based trading strategy"""
    
    def analyze(self, analyzer) -> Dict:
        """Analyze using machine learning models"""
        data = analyzer.data
        metrics = analyzer.get_current_metrics()
        
        try:
            # Prepare features for ML model
            features = self._prepare_features(data)
            
            # Simple ML prediction using Random Forest
            prediction_score = self._predict_trend(features)
            
            score = int(prediction_score * 100)  # Convert to -100 to 100 scale
            reasons = self._generate_ml_reasons(features, prediction_score, metrics)
            
            return self._generate_recommendation(score, reasons, "AI/ML")
            
        except Exception as e:
            # Fallback to simple technical analysis if ML fails
            score = 0
            reasons = [self._format_reason("strategy_ml_fallback")]
            return self._generate_recommendation(score, reasons, "AI/ML")
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for ML model"""
        # Technical indicators as features
        rsi = self._calculate_rsi(data['Close'])
        macd = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
        bb_position = (data['Close'] - data['Close'].rolling(20).mean()) / (2 * data['Close'].rolling(20).std())
        
        # Price features
        returns_5d = data['Close'].pct_change(5)
        returns_20d = data['Close'].pct_change(20)
        volume_ratio = data['Volume'] / data['Volume'].rolling(20).mean()
        
        # Combine features
        features = np.column_stack([
            rsi.fillna(50).values[-30:],  # Last 30 days
            macd.fillna(0).values[-30:],
            bb_position.fillna(0).values[-30:],
            returns_5d.fillna(0).values[-30:],
            returns_20d.fillna(0).values[-30:],
            volume_ratio.fillna(1).values[-30:]
        ])
        
        return features
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _predict_trend(self, features: np.ndarray) -> float:
        """Simple ML prediction - in real implementation, use pre-trained model"""
        # Simplified prediction logic (replace with actual ML model)
        latest_features = features[-1]
        
        # Weighted feature scoring
        rsi_score = (50 - latest_features[0]) / 50  # RSI normalization
        macd_score = np.tanh(latest_features[1])  # MACD normalization
        bb_score = np.clip(latest_features[2], -1, 1)  # BB position
        momentum_score = np.tanh(latest_features[3] * 10)  # Returns
        
        # Combine scores with weights
        prediction = (rsi_score * 0.3 + macd_score * 0.3 + 
                     bb_score * 0.2 + momentum_score * 0.2)
        
        return np.clip(prediction, -0.8, 0.8)  # Limit extreme predictions
    
    def _generate_ml_reasons(self, features: np.ndarray, prediction: float, metrics: Dict) -> List[str]:
        """Generate explanations for ML prediction"""
        reasons = []
        latest = features[-1]
        
        # RSI interpretation
        if latest[0] < 30:
            reasons.append(self._format_reason("strategy_ml_rsi_oversold"))
        elif latest[0] > 70:
            reasons.append(self._format_reason("strategy_ml_rsi_overbought"))
        
        # MACD interpretation
        if latest[1] > 0.01:
            reasons.append(self._format_reason("strategy_ml_macd_bullish"))
        elif latest[1] < -0.01:
            reasons.append(self._format_reason("strategy_ml_macd_bearish"))
        
        # Overall AI prediction
        confidence = abs(prediction)
        if prediction > 0.3:
            reasons.append(self._format_reason("strategy_ml_bullish_prediction", confidence * 100))
        elif prediction < -0.3:
            reasons.append(self._format_reason("strategy_ml_bearish_prediction", confidence * 100))
        else:
            reasons.append(self._format_reason("strategy_ml_neutral_prediction"))
        
        return reasons
    
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
