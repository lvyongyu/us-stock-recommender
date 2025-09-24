"""
Abstract base class for trading strategies
"""
from abc import ABC, abstractmethod
from typing import Dict, List


class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, lang_config):
        self.lang_config = lang_config
        self.strategy_name = self.__class__.__name__
    
    @abstractmethod
    def analyze(self, analyzer) -> Dict:
        """
        Analyze stock data and generate recommendation
        
        Args:
            analyzer: StockAnalyzer instance with fetched data
            
        Returns:
            Dict containing:
            - action: str (buy/sell/hold)
            - confidence: float (0.0-1.0)
            - reasoning: List[str] (detailed reasons)
            - score: int (overall score)
        """
        pass
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return self.strategy_name
