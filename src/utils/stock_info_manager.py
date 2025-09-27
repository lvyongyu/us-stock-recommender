"""
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
    """Stock information manager"""
    
    def __init__(self):
        self.stock_cache_file = os.path.expanduser("~/.stock_recommender/stock_info_cache.json")
        self.ensure_cache_dir()
        self.stock_info_cache = self._load_cache()
    
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        cache_dir = os.path.dirname(self.stock_cache_file)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
    
    def _load_cache(self) -> Dict:
        """Load stock information cache"""
        try:
            if os.path.exists(self.stock_cache_file):
                with open(self.stock_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save stock information cache"""
        try:
            with open(self.stock_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.stock_info_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search stocks by symbol
        Args:
            query: Stock symbol to search
            limit: Maximum number of results (kept for compatibility)
        Returns:
            List containing the stock if found, empty list otherwise
        """
        if not query or len(query.strip()) < 1:
            return []  # Return empty list when no search query
        
        query = query.upper().strip()
        
        # Try to get stock information for the entered symbol
        stock_info = self.get_stock_info(query)
        if stock_info and stock_info.get("name") and stock_info["name"] != query:
            # Only return if we got a valid name (not just the symbol itself)
            return [{
                "symbol": stock_info["symbol"],
                "name": stock_info["name"],
                "sector": stock_info["sector"]
            }]
        
        return []
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed stock information
        Args:
            symbol: Stock symbol
        Returns:
            Stock information dictionary
        """
        symbol = symbol.upper().strip()
        
        # Check cache
        cache_key = f"{symbol}_{datetime.now().strftime('%Y-%m-%d')}"
        if cache_key in self.stock_info_cache:
            return self.stock_info_cache[cache_key]
        
        try:
            # Get data from yfinance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get historical data for current price calculation
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
            
            # Cache the result
            self.stock_info_cache[cache_key] = stock_info
            self._save_cache()
            
            return stock_info
            
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def format_stock_display(self, stock_info: Dict) -> str:
        """Format stock display information"""
        symbol = stock_info["symbol"]
        name = stock_info["name"]
        sector = stock_info.get("sector", "Unknown")
        
        # If real-time price information is available
        if "current_price" in stock_info and stock_info["current_price"]:
            price = stock_info["current_price"]
            return f"{symbol} - {name} ({sector}) - ${price:.2f}"
        else:
            return f"{symbol} - {name} ({sector})"

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_manager():
    """Get stock information manager instance"""
    return StockInfoManager()