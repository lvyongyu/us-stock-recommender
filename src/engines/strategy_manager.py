"""
Strategy manager for combining multiple trading strategies
"""
from typing import Dict, List
from ..strategies.technical_strategy import TechnicalIndicatorStrategy
from ..strategies.quantitative_strategy import QuantitativeStrategy
from ..strategies.aiml_strategy import AIMLStrategy


class StrategyManager:
    """Trading strategy manager - manages multiple strategies and combines their recommendations"""
    
    def __init__(self, lang_config):
        self.lang_config = lang_config
        self.strategies = {
            'technical': TechnicalIndicatorStrategy(lang_config),
            'quantitative': QuantitativeStrategy(lang_config), 
            'ai': AIMLStrategy(lang_config)
        }
        
        # Default weights for combining strategies
        self.default_weights = {
            'technical': 0.4,
            'quantitative': 0.35,
            'ai': 0.25
        }
    
    def get_recommendation(self, analyzer, strategy_types: List[str] = None) -> Dict:
        """Get recommendation from specified strategies or all strategies"""
        
        if strategy_types is None or 'all' in strategy_types:
            strategy_types = list(self.strategies.keys())
        
        # Single strategy
        if len(strategy_types) == 1:
            strategy_type = strategy_types[0]
            if strategy_type in self.strategies:
                result = self.strategies[strategy_type].analyze(analyzer)
                result['strategy_name'] = self.lang_config.get(f"strategy_{strategy_type}")
                return result
            else:
                raise ValueError(f"Unknown strategy: {strategy_type}")
        
        # Multiple strategies - combine results
        return self._combine_strategies(analyzer, strategy_types)
    
    def _combine_strategies(self, analyzer, strategy_types: List[str]) -> Dict:
        """Combine multiple strategy recommendations"""
        results = {}
        total_weight = 0
        
        # Get individual strategy results
        for strategy_type in strategy_types:
            if strategy_type in self.strategies:
                try:
                    result = self.strategies[strategy_type].analyze(analyzer)
                    results[strategy_type] = result
                    total_weight += self.default_weights.get(strategy_type, 0.33)
                except Exception as e:
                    print(f"Warning: {strategy_type} strategy failed: {e}")
                    continue
        
        if not results:
            raise ValueError("No strategies could be executed successfully")
        
        # Normalize weights
        for strategy_type in results:
            weight = self.default_weights.get(strategy_type, 0.33)
            results[strategy_type]['weight'] = weight / total_weight
        
        # Combine scores
        combined_score = 0
        combined_confidence = 0
        all_reasons = []
        
        for strategy_type, result in results.items():
            weight = result['weight']
            combined_score += result['score'] * weight
            combined_confidence += result['confidence'] * weight
            
            # Add weighted strategy reasons
            strategy_name = self.lang_config.get(f"strategy_{strategy_type}")
            weight_text = self.lang_config.get(f"strategy_weight_{strategy_type}").format(int(weight * 100))
            all_reasons.extend(result['reasons'])
            all_reasons.append(weight_text)
        
        # Determine final action based on combined score
        combined_score = int(combined_score)
        
        if combined_score >= 60:
            action = "strong_buy"
        elif combined_score >= 25:
            action = "buy"
        elif combined_score >= -25:
            action = "hold"
        elif combined_score >= -60:
            action = "sell"
        else:
            action = "strong_sell"
        
        # Add consensus information
        actions = [result['action'] for result in results.values()]
        unique_actions = len(set(actions))
        
        if unique_actions == 1:
            consensus_reason = self.lang_config.get("strategy_consensus_strong")
        elif unique_actions == 2:
            consensus_reason = self.lang_config.get("strategy_consensus_moderate")
        else:
            consensus_reason = self.lang_config.get("strategy_consensus_mixed")
        
        all_reasons.insert(0, consensus_reason)
        
        return {
            'action': action,
            'confidence': round(combined_confidence, 2),
            'score': combined_score,
            'reasons': all_reasons,
            'strategy': self.lang_config.get("strategy_combined"),
            'strategy_name': self.lang_config.get("strategy_combined"),
            'individual_results': results
        }
