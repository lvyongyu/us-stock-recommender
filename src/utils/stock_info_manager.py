"""
股票信息数据库和动态搜索功能
Stock Information Database and Dynamic Search Functions
"""

import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple
import json
import os
from datetime import datetime

class StockInfoManager:
    """股票信息管理器"""
    
    def __init__(self):
        self.stock_cache_file = os.path.expanduser("~/.stock_recommender/stock_info_cache.json")
        self.ensure_cache_dir()
        self.popular_stocks = self._get_popular_stocks()
        self.stock_info_cache = self._load_cache()
    
    def ensure_cache_dir(self):
        """确保缓存目录存在"""
        cache_dir = os.path.dirname(self.stock_cache_file)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
    
    def _get_popular_stocks(self) -> List[Dict]:
        """获取常用股票列表"""
        return [
            # 科技股
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Technology"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Technology"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Technology"},
            {"symbol": "ADBE", "name": "Adobe Inc.", "sector": "Technology"},
            {"symbol": "CRM", "name": "Salesforce Inc.", "sector": "Technology"},
            
            # 金融股
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial"},
            {"symbol": "BAC", "name": "Bank of America Corp.", "sector": "Financial"},
            {"symbol": "WFC", "name": "Wells Fargo & Company", "sector": "Financial"},
            {"symbol": "GS", "name": "Goldman Sachs Group Inc.", "sector": "Financial"},
            {"symbol": "MS", "name": "Morgan Stanley", "sector": "Financial"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financial"},
            {"symbol": "MA", "name": "Mastercard Inc.", "sector": "Financial"},
            
            # 医疗保健
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
            {"symbol": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare"},
            {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare"},
            {"symbol": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare"},
            {"symbol": "MRK", "name": "Merck & Co. Inc.", "sector": "Healthcare"},
            
            # 消费品
            {"symbol": "KO", "name": "Coca-Cola Company", "sector": "Consumer"},
            {"symbol": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer"},
            {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer"},
            {"symbol": "PG", "name": "Procter & Gamble Company", "sector": "Consumer"},
            {"symbol": "HD", "name": "Home Depot Inc.", "sector": "Consumer"},
            
            # 能源股
            {"symbol": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy"},
            {"symbol": "CVX", "name": "Chevron Corporation", "sector": "Energy"},
            
            # 其他
            {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc.", "sector": "Financial"},
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "sector": "ETF"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "sector": "ETF"},
        ]
    
    def _load_cache(self) -> Dict:
        """加载股票信息缓存"""
        try:
            if os.path.exists(self.stock_cache_file):
                with open(self.stock_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load cache: {e}")
        return {}
    
    def _save_cache(self):
        """保存股票信息缓存"""
        try:
            with open(self.stock_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.stock_info_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索股票
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
        Returns:
            匹配的股票列表
        """
        if not query or len(query.strip()) < 1:
            return self.popular_stocks[:limit]
        
        query = query.upper().strip()
        matches = []
        
        # 搜索流行股票列表
        for stock in self.popular_stocks:
            symbol = stock["symbol"]
            name = stock["name"].upper()
            
            # 精确匹配股票代码
            if symbol.startswith(query):
                matches.append(stock)
            # 模糊匹配公司名称
            elif query in name:
                matches.append(stock)
        
        # 去重并限制数量
        seen_symbols = set()
        unique_matches = []
        for stock in matches:
            if stock["symbol"] not in seen_symbols:
                unique_matches.append(stock)
                seen_symbols.add(stock["symbol"])
                if len(unique_matches) >= limit:
                    break
        
        return unique_matches
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        获取股票详细信息
        Args:
            symbol: 股票代码
        Returns:
            股票信息字典
        """
        symbol = symbol.upper().strip()
        
        # 检查缓存
        cache_key = f"{symbol}_{datetime.now().strftime('%Y-%m-%d')}"
        if cache_key in self.stock_info_cache:
            return self.stock_info_cache[cache_key]
        
        try:
            # 从 yfinance 获取数据
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取历史数据用于计算当前价格
            hist = ticker.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            
            stock_info = {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "current_price": float(current_price) if current_price else None,
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap", None),
                "pe_ratio": info.get("forwardPE", None),
                "dividend_yield": info.get("dividendYield", None),
                "beta": info.get("beta", None),
                "last_updated": datetime.now().isoformat(),
                "description": info.get("longBusinessSummary", "")[:200] + "..." if info.get("longBusinessSummary") else ""
            }
            
            # 缓存结果
            self.stock_info_cache[cache_key] = stock_info
            self._save_cache()
            
            return stock_info
            
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def format_stock_display(self, stock_info: Dict) -> str:
        """格式化股票显示信息"""
        symbol = stock_info["symbol"]
        name = stock_info["name"]
        sector = stock_info.get("sector", "Unknown")
        
        # 如果有实时价格信息
        if "current_price" in stock_info and stock_info["current_price"]:
            price = stock_info["current_price"]
            return f"{symbol} - {name} ({sector}) - ${price:.2f}"
        else:
            return f"{symbol} - {name} ({sector})"

@st.cache_data(ttl=3600)  # 缓存1小时
def get_stock_manager():
    """获取股票信息管理器实例"""
    return StockInfoManager()