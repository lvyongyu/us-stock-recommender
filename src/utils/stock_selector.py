"""
Dynamic Stock Search and Selection Component
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple
from .stock_info_manager import StockInfoManager, get_stock_manager

def create_dynamic_stock_selector(
    key: str = "stock_selector",
    placeholder: str = "Search stock symbol or company name...",
    help_text: str = "Enter stock symbol (e.g. AAPL) or company name to search"
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Create dynamic stock selector
    
    Args:
        key: Component unique identifier
        placeholder: Input field placeholder
        help_text: Help text
    
    Returns:
        (selected_symbol, stock_info): Selected stock symbol and detailed information
    """
    
    # Get stock manager
    stock_manager = get_stock_manager()
    
    # Create search input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Stock Search",
            placeholder=placeholder,
            help=help_text,
            key=f"{key}_search"
        )
    
    with col2:
        search_button = st.button("🔍 Search", key=f"{key}_button")
    
    # Initialize session state
    if f"{key}_results" not in st.session_state:
        st.session_state[f"{key}_results"] = []
    if f"{key}_selected" not in st.session_state:
        st.session_state[f"{key}_selected"] = None
    if f"{key}_stock_info" not in st.session_state:
        st.session_state[f"{key}_stock_info"] = {}
    
    # Real-time search (when input changes)
    if search_query and len(search_query.strip()) > 0:
        # Execute search
        search_results = stock_manager.search_stocks(search_query, limit=15)
        st.session_state[f"{key}_results"] = search_results
    elif not search_query:
        # Show popular stocks
        st.session_state[f"{key}_results"] = stock_manager.search_stocks("", limit=10)
    
    # Display search results
    if st.session_state[f"{key}_results"]:
        st.markdown("### 📈 Search Results")
        
        # Create results display area
        results_container = st.container()
        
        with results_container:
            # Use columns to create grid layout
            cols_per_row = 2
            results = st.session_state[f"{key}_results"]
            
            for i in range(0, len(results), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(results):
                        stock = results[i + j]
                        
                        with col:
                            # Create stock card
                            _create_stock_card(stock, key, stock_manager)
    
    # Display selected stock detailed information
    if st.session_state[f"{key}_selected"]:
        selected_symbol = st.session_state[f"{key}_selected"]
        stock_info = st.session_state[f"{key}_stock_info"].get(selected_symbol)
        
        if stock_info:
            _display_selected_stock_info(stock_info)
            return selected_symbol, stock_info
    
    return None, None

def _create_stock_card(stock: Dict, key: str, stock_manager: StockInfoManager):
    """Create stock card"""
    symbol = stock["symbol"]
    name = stock["name"]
    sector = stock.get("sector", "Unknown")
    
    # Create card container
    with st.container():
        # Stock basic information
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 10px; 
            margin: 5px 0;
            background-color: #f9f9f9;
            cursor: pointer;
        ">
            <strong style="color: #1f77b4; font-size: 16px;">{symbol}</strong><br>
            <span style="font-size: 12px; color: #666;">{name}</span><br>
            <span style="font-size: 10px; color: #999;">{sector}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Select button
        if st.button(f"Select {symbol}", key=f"{key}_select_{symbol}", help=f"Select {name}"):
            # Get stock detailed information
            with st.spinner(f"Getting detailed information for {symbol}..."):
                stock_info = stock_manager.get_stock_info(symbol)
                
                if stock_info:
                    st.session_state[f"{key}_selected"] = symbol
                    st.session_state[f"{key}_stock_info"][symbol] = stock_info
                    st.rerun()
                else:
                    st.error(f"Unable to get detailed information for {symbol}")

def _display_selected_stock_info(stock_info: Dict):
    """Display selected stock detailed information"""
    st.markdown("### 📊 Selected Stock Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Stock Symbol",
            value=stock_info["symbol"]
        )
    
    with col2:
        if stock_info.get("current_price"):
            st.metric(
                label="Current Price",
                value=f"${stock_info['current_price']:.2f}",
                delta=None
            )
    
    with col3:
        st.metric(
            label="Sector",
            value=stock_info.get("sector", "Unknown")
        )
    
    # Company name and description
    st.markdown(f"**Company Name**: {stock_info['name']}")
    
    if stock_info.get("description"):
        with st.expander("📝 Company Profile"):
            st.write(stock_info["description"])
    
    # Other financial metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if stock_info.get("market_cap"):
            market_cap_b = stock_info["market_cap"] / 1e9
            st.metric("Market Cap", f"${market_cap_b:.1f}B")
    
    with col2:
        if stock_info.get("pe_ratio"):
            st.metric("P/E Ratio", f"{stock_info['pe_ratio']:.2f}")
    
    with col3:
        if stock_info.get("dividend_yield"):
            dividend_pct = stock_info["dividend_yield"] * 100
            st.metric("Dividend Yield", f"{dividend_pct:.2f}%")
    
    with col4:
        if stock_info.get("beta"):
            st.metric("Beta", f"{stock_info['beta']:.2f}")

def create_stock_weight_input(selected_symbol: str, key: str = "weight_input") -> Optional[float]:
    """
    Create stock weight input component
    
    Args:
        selected_symbol: Selected stock symbol
        key: Component unique identifier
    
    Returns:
        Input weight value
    """
    if not selected_symbol:
        return None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        weight = st.number_input(
            f"Set weight for {selected_symbol}",
            min_value=0.01,
            max_value=1.00,
            value=0.10,
            step=0.01,
            format="%.2f",
            help="Weight range: 0.01 - 1.00 (1% - 100%)",
            key=f"{key}_weight"
        )
    
    with col2:
        weight_pct = weight * 100
        st.metric("Weight Percentage", f"{weight_pct:.1f}%")
    
    return weight