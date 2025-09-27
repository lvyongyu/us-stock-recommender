"""
动态股票搜索和选择组件
Dynamic Stock Search and Selection Component
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple
from .stock_info_manager import StockInfoManager, get_stock_manager

def create_dynamic_stock_selector(
    key: str = "stock_selector",
    placeholder: str = "搜索股票代码或公司名称...",
    help_text: str = "输入股票代码（如 AAPL）或公司名称进行搜索"
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    创建动态股票选择器
    
    Args:
        key: 组件唯一标识
        placeholder: 输入框占位符
        help_text: 帮助文本
    
    Returns:
        (selected_symbol, stock_info): 选中的股票代码和详细信息
    """
    
    # 获取股票管理器
    stock_manager = get_stock_manager()
    
    # 创建搜索输入框
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "股票搜索",
            placeholder=placeholder,
            help=help_text,
            key=f"{key}_search"
        )
    
    with col2:
        search_button = st.button("🔍 搜索", key=f"{key}_button")
    
    # 初始化session state
    if f"{key}_results" not in st.session_state:
        st.session_state[f"{key}_results"] = []
    if f"{key}_selected" not in st.session_state:
        st.session_state[f"{key}_selected"] = None
    if f"{key}_stock_info" not in st.session_state:
        st.session_state[f"{key}_stock_info"] = {}
    
    # 实时搜索（当输入发生变化时）
    if search_query and len(search_query.strip()) > 0:
        # 执行搜索
        search_results = stock_manager.search_stocks(search_query, limit=15)
        st.session_state[f"{key}_results"] = search_results
    elif not search_query:
        # 显示热门股票
        st.session_state[f"{key}_results"] = stock_manager.search_stocks("", limit=10)
    
    # 显示搜索结果
    if st.session_state[f"{key}_results"]:
        st.markdown("### 📈 搜索结果")
        
        # 创建结果显示区域
        results_container = st.container()
        
        with results_container:
            # 使用columns来创建网格布局
            cols_per_row = 2
            results = st.session_state[f"{key}_results"]
            
            for i in range(0, len(results), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(results):
                        stock = results[i + j]
                        
                        with col:
                            # 创建股票卡片
                            _create_stock_card(stock, key, stock_manager)
    
    # 显示选中的股票详细信息
    if st.session_state[f"{key}_selected"]:
        selected_symbol = st.session_state[f"{key}_selected"]
        stock_info = st.session_state[f"{key}_stock_info"].get(selected_symbol)
        
        if stock_info:
            _display_selected_stock_info(stock_info)
            return selected_symbol, stock_info
    
    return None, None

def _create_stock_card(stock: Dict, key: str, stock_manager: StockInfoManager):
    """创建股票卡片"""
    symbol = stock["symbol"]
    name = stock["name"]
    sector = stock.get("sector", "Unknown")
    
    # 创建卡片容器
    with st.container():
        # 股票基本信息
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
        
        # 选择按钮
        if st.button(f"选择 {symbol}", key=f"{key}_select_{symbol}", help=f"选择 {name}"):
            # 获取股票详细信息
            with st.spinner(f"正在获取 {symbol} 的详细信息..."):
                stock_info = stock_manager.get_stock_info(symbol)
                
                if stock_info:
                    st.session_state[f"{key}_selected"] = symbol
                    st.session_state[f"{key}_stock_info"][symbol] = stock_info
                    st.rerun()
                else:
                    st.error(f"无法获取 {symbol} 的详细信息")

def _display_selected_stock_info(stock_info: Dict):
    """显示选中股票的详细信息"""
    st.markdown("### 📊 选中股票详情")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="股票代码",
            value=stock_info["symbol"]
        )
    
    with col2:
        if stock_info.get("current_price"):
            st.metric(
                label="当前价格",
                value=f"${stock_info['current_price']:.2f}",
                delta=None
            )
    
    with col3:
        st.metric(
            label="行业",
            value=stock_info.get("sector", "Unknown")
        )
    
    # 公司名称和描述
    st.markdown(f"**公司名称**: {stock_info['name']}")
    
    if stock_info.get("description"):
        with st.expander("📝 公司简介"):
            st.write(stock_info["description"])
    
    # 其他财务指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if stock_info.get("market_cap"):
            market_cap_b = stock_info["market_cap"] / 1e9
            st.metric("市值", f"${market_cap_b:.1f}B")
    
    with col2:
        if stock_info.get("pe_ratio"):
            st.metric("P/E 比率", f"{stock_info['pe_ratio']:.2f}")
    
    with col3:
        if stock_info.get("dividend_yield"):
            dividend_pct = stock_info["dividend_yield"] * 100
            st.metric("股息收益率", f"{dividend_pct:.2f}%")
    
    with col4:
        if stock_info.get("beta"):
            st.metric("贝塔系数", f"{stock_info['beta']:.2f}")

def create_stock_weight_input(selected_symbol: str, key: str = "weight_input") -> Optional[float]:
    """
    创建股票权重输入组件
    
    Args:
        selected_symbol: 选中的股票代码
        key: 组件唯一标识
    
    Returns:
        输入的权重值
    """
    if not selected_symbol:
        return None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        weight = st.number_input(
            f"设置 {selected_symbol} 的权重",
            min_value=0.01,
            max_value=1.00,
            value=0.10,
            step=0.01,
            format="%.2f",
            help="权重范围: 0.01 - 1.00 (1% - 100%)",
            key=f"{key}_weight"
        )
    
    with col2:
        weight_pct = weight * 100
        st.metric("权重百分比", f"{weight_pct:.1f}%")
    
    return weight