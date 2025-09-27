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
        self.popular_stocks = self._get_popular_stocks()
        self.stock_info_cache = self._load_cache()
    
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        cache_dir = os.path.dirname(self.stock_cache_file)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
    
    def _get_popular_stocks(self) -> List[Dict]:
        """Get popular stocks list"""
        return [
            # Technology stocks
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
            
            # Financial stocks
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial"},
            {"symbol": "BAC", "name": "Bank of America Corp.", "sector": "Financial"},
            {"symbol": "WFC", "name": "Wells Fargo & Company", "sector": "Financial"},
            {"symbol": "GS", "name": "Goldman Sachs Group Inc.", "sector": "Financial"},
            {"symbol": "MS", "name": "Morgan Stanley", "sector": "Financial"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financial"},
            {"symbol": "MA", "name": "Mastercard Inc.", "sector": "Financial"},
            
            # Healthcare stocks
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
            {"symbol": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare"},
            {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare"},
            {"symbol": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare"},
            {"symbol": "MRK", "name": "Merck & Co. Inc.", "sector": "Healthcare"},
            
            # Consumer stocks
            {"symbol": "KO", "name": "Coca-Cola Company", "sector": "Consumer"},
            {"symbol": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer"},
            {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer"},
            {"symbol": "PG", "name": "Procter & Gamble Company", "sector": "Consumer"},
            {"symbol": "HD", "name": "Home Depot Inc.", "sector": "Consumer"},
            
            # Energy stocks
            {"symbol": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy"},
            {"symbol": "CVX", "name": "Chevron Corporation", "sector": "Energy"},
            
            # Others
            {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc.", "sector": "Financial"},
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "sector": "ETF"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "sector": "ETF"},
        ]
    
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
        Search stocks
        Args:
            query: Search keyword
            limit: Maximum number of results
        Returns:
            List of matching stocks
        """
        if not query or len(query.strip()) < 1:
            return []  # Return empty list when no search query
        
        query = query.upper().strip()
        matches = []
        
        # Search popular stocks list
        for stock in self.popular_stocks:
            symbol = stock["symbol"]
            name = stock["name"].upper()
            
            # Exact match for stock symbol
            if symbol.startswith(query):
                matches.append(stock)
            # Fuzzy match for company name
            elif query in name:
                matches.append(stock)
        
        # Remove duplicates and limit results
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