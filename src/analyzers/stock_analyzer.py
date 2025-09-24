"""
Stock analyzer module for fetching and analyzing stock data
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from ..languages.config import LanguageConfig


class StockAnalyzer:
    """Stock analyzer - responsible for fetching and analyzing stock data"""
    
    def __init__(self, symbol: str, lang_config: Optional[LanguageConfig] = None):
        self.symbol = symbol.upper()
        self.ticker = yf.Ticker(self.symbol)
        self.data = None
        self.lang_config = lang_config or LanguageConfig('en')
        
    def fetch_data(self, period: str = "1y") -> pd.DataFrame:
        """Fetch historical stock data"""
        try:
            self.data = self.ticker.history(period=period)
            if self.data.empty:
                raise ValueError(self.lang_config.get("no_data_found").format(self.symbol))
            return self.data
        except Exception as e:
            raise Exception(self.lang_config.get("fetch_data_failed").format(str(e)))
    
    def calculate_technical_indicators(self) -> Dict:
        """Calculate technical indicators"""
        if self.data is None or self.data.empty:
            raise ValueError(self.lang_config.get("data_required"))
            
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
        """Get current key metrics for the stock"""
        if self.data is None or self.data.empty:
            raise ValueError(self.lang_config.get("data_required"))
            
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
