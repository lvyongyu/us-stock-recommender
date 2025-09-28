"""
Portfolio Management Web Interface

A modern web-based portfolio management system built with Streamlit.
Provides intuitive interface for creating, managing, and analyzing investment portfolios.

Features:
- Portfolio creation and management
- Stock position tracking
- Real-time portfolio analysis
- Interactive charts and visualizations
- Risk assessment and recommendations
- Portfolio comparison tools
- Multi-language support

Run with: streamlit run portfolio_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import portfolio management components
try:
    from src.portfolio import PortfolioManager, PortfolioAnalyzer, StrategyType
    from src.portfolio.exceptions import PortfolioError
    from src.utils.stock_selector import create_dynamic_stock_selector, create_stock_weight_input
    from src.utils.stock_info_manager import get_stock_manager
except ImportError as e:
    st.error(f"Failed to import portfolio components: {e}")
    st.stop()

# Import simulation components
try:
    from src.simulation.account_manager import SimulationAccountManager
    from src.simulation.trader import VirtualTrader
    from src.simulation.backtest_engine import BacktestEngine
    from src.simulation.automated_trader import AutomatedTrader
    from src.simulation.models import TransactionType, OrderType
except ImportError as e:
    st.warning(f"Simulation components not available: {e}")
    SIMULATION_AVAILABLE = False
else:
    SIMULATION_AVAILABLE = True


# Page configuration
st.set_page_config(
    page_title="Portfolio Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .success-alert {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    
    .warning-alert {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #ffeaa7;
    }
    
    .error-alert {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'portfolio_manager' not in st.session_state:
        st.session_state.portfolio_manager = PortfolioManager()
    
    if 'portfolio_analyzer' not in st.session_state:
        st.session_state.portfolio_analyzer = PortfolioAnalyzer(language='en')
    
    if 'selected_portfolio' not in st.session_state:
        st.session_state.selected_portfolio = None
    
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}
    
    # Initialize stock information cache for future K-line and other features
    if 'portfolio_stock_cache' not in st.session_state:
        st.session_state.portfolio_stock_cache = {}
    
    # Initialize stock manager cache
    if 'stock_manager' not in st.session_state:
        st.session_state.stock_manager = get_stock_manager()


# Utility functions
def get_strategy_color(strategy_type: StrategyType) -> str:
    """Get color for strategy type."""
    colors = {
        StrategyType.CONSERVATIVE: "#28a745",
        StrategyType.BALANCED: "#ffc107", 
        StrategyType.AGGRESSIVE: "#dc3545",
        StrategyType.CUSTOM: "#6c757d"
    }
    return colors.get(strategy_type, "#6c757d")


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage with proper styling."""
    return f"{value:.{decimals}f}%"


def format_currency(value: float) -> str:
    """Format currency value."""
    return f"${value:,.2f}"


def create_portfolio_overview_chart(portfolio):
    """Create portfolio holdings overview chart."""
    if not portfolio.holdings:
        return None
    
    # Prepare data
    symbols = [h.symbol for h in portfolio.holdings]
    weights = [h.weight for h in portfolio.holdings]
    
    # Create pie chart
    fig = px.pie(
        values=weights,
        names=symbols,
        title=f"{portfolio.name} - Holdings Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Weight: %{percent}<br>Value: %{value:.1f}%<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_risk_return_chart(portfolios_analysis: List[Dict]):
    """Create risk-return scatter plot for portfolio comparison."""
    if not portfolios_analysis:
        return None
    
    # Prepare data
    names = []
    returns = []
    risks = []
    strategies = []
    
    for analysis in portfolios_analysis:
        portfolio_info = analysis.get('portfolio_info', {})
        metrics = analysis.get('portfolio_metrics', {})
        
        names.append(portfolio_info.get('name', 'Unknown'))
        returns.append(metrics.get('expected_return', 0) * 100)
        risks.append(metrics.get('risk_score', 0.5) * 100)
        strategies.append(portfolio_info.get('strategy', 'balanced'))
    
    # Create scatter plot
    fig = px.scatter(
        x=risks,
        y=returns,
        text=names,
        color=strategies,
        title="Portfolio Risk vs Expected Return",
        labels={
            'x': 'Risk Score (%)',
            'y': 'Expected Return (%)',
            'color': 'Strategy'
        },
        color_discrete_map={
            'conservative': '#28a745',
            'balanced': '#ffc107',
            'aggressive': '#dc3545'
        }
    )
    
    fig.update_traces(
        textposition="top center",
        marker=dict(size=12)
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Risk Score (%)",
        yaxis_title="Expected Return (%)"
    )
    
    return fig


def create_holdings_comparison_chart(portfolio):
    """Create current vs target weights comparison chart."""
    if not portfolio.holdings:
        return None
    
    # Prepare data
    symbols = []
    current_weights = []
    target_weights = []
    
    for holding in portfolio.holdings:
        symbols.append(holding.symbol)
        current_weights.append(holding.weight)
        target_weights.append(holding.target_weight if holding.target_weight else holding.weight)
    
    # Create grouped bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Current Weight',
        x=symbols,
        y=current_weights,
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Target Weight', 
        x=symbols,
        y=target_weights,
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title=f"{portfolio.name} - Current vs Target Weights",
        xaxis_title="Stock Symbol",
        yaxis_title="Weight (%)",
        barmode='group',
        height=400
    )
    
    return fig


# Page functions
def show_dashboard():
    """Show main dashboard page."""
    st.markdown('<h1 class="main-header">📊 Portfolio Management Dashboard</h1>', unsafe_allow_html=True)
    
    manager = st.session_state.portfolio_manager
    analyzer = st.session_state.portfolio_analyzer
    
    # Get all portfolios
    portfolios = manager.list_portfolios()
    
    if not portfolios:
        st.info("🎯 Welcome! Create your first portfolio to get started.")
        return
    
    # Portfolio overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Portfolios", len(portfolios))
    
    with col2:
        total_holdings = sum(len(p.holdings) for p in portfolios)
        st.metric("Total Holdings", total_holdings)
    
    with col3:
        strategy_counts = {}
        for p in portfolios:
            strategy = p.strategy_type.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        most_common = max(strategy_counts.items(), key=lambda x: x[1]) if strategy_counts else ("None", 0)
        st.metric("Most Common Strategy", most_common[0].title())
    
    with col4:
        # Calculate average diversification
        total_div = 0
        valid_portfolios = 0
        for p in portfolios:
            if p.holdings:
                try:
                    analysis = analyzer.analyze_portfolio(p)
                    total_div += analysis['portfolio_metrics']['diversification_score']
                    valid_portfolios += 1
                except:
                    pass
        avg_div = total_div / valid_portfolios if valid_portfolios > 0 else 0
        st.metric("Avg Diversification", f"{avg_div:.1%}")
    
    # Recent portfolios section
    st.subheader("📈 Portfolio Overview")
    
    # Create portfolio summary table
    portfolio_data = []
    for portfolio in portfolios[:5]:  # Show top 5 portfolios
        try:
            analysis = analyzer.analyze_portfolio(portfolio)
            expected_return = analysis.get('portfolio_metrics', {}).get('expected_return', 0)
            risk_level = analysis.get('risk_assessment', {}).get('risk_level', 'Unknown')
            recommendation = analysis.get('overall_recommendation', {}).get('recommendation', 'N/A')
            
            portfolio_data.append({
                'Name': portfolio.name,
                'Strategy': portfolio.strategy_type.value.title(),
                'Holdings': len(portfolio.holdings),
                'Total Weight': f"{portfolio.total_weight:.1%}",
                'Expected Return': f"{expected_return:.1%}" if expected_return is not None else "N/A",
                'Risk Level': risk_level,
                'Recommendation': recommendation
            })
        except Exception as e:
            portfolio_data.append({
                'Name': portfolio.name,
                'Strategy': portfolio.strategy_type.value.title(),
                'Holdings': len(portfolio.holdings),
                'Total Weight': f"{portfolio.total_weight:.1%}",
                'Expected Return': 'N/A',
                'Risk Level': 'Unknown',
                'Recommendation': 'Error'
            })
    
    if portfolio_data:
        df = pd.DataFrame(portfolio_data)
        st.dataframe(df, use_container_width=True)
    
    # Portfolio performance comparison
    if len(portfolios) > 1:
        st.subheader("🔄 Portfolio Comparison")
        
        # Analyze all portfolios for comparison
        analyses = []
        for portfolio in portfolios:
            try:
                analysis = analyzer.analyze_portfolio(portfolio)
                analyses.append(analysis)
            except:
                continue
        
        if len(analyses) > 1:
            fig = create_risk_return_chart(analyses)
            if fig:
                st.plotly_chart(fig, use_container_width=True)


def show_portfolio_management():
    """Show portfolio management page."""
    st.markdown('<h1 class="main-header">💼 Portfolio Management</h1>', unsafe_allow_html=True)
    
    manager = st.session_state.portfolio_manager
    
    # Tabs for different management functions
    tab1, tab2, tab3 = st.tabs(["📝 Create Portfolio", "✏️ Edit Portfolio", "📊 Portfolio Details"])
    
    with tab1:
        st.subheader("Create New Portfolio")
        
        with st.form("create_portfolio"):
            col1, col2 = st.columns(2)
            
            with col1:
                portfolio_name = st.text_input("Portfolio Name", placeholder="e.g., Tech Growth Portfolio")
                strategy = st.selectbox(
                    "Investment Strategy",
                    options=[StrategyType.CONSERVATIVE, StrategyType.BALANCED, StrategyType.AGGRESSIVE, StrategyType.CUSTOM],
                    format_func=lambda x: x.value.title()
                )
            
            with col2:
                description = st.text_area(
                    "Description", 
                    placeholder="Brief description of your investment strategy...",
                    height=100
                )
            
            submitted = st.form_submit_button("Create Portfolio", use_container_width=True)
            
            if submitted:
                if portfolio_name:
                    try:
                        portfolio = manager.create_portfolio(
                            name=portfolio_name,
                            description=description,
                            strategy_type=strategy
                        )
                        st.success(f"✅ Portfolio '{portfolio_name}' created successfully!")
                        st.balloons()
                        st.rerun()
                    except PortfolioError as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Please provide a portfolio name.")
    
    with tab2:
        st.subheader("Edit Existing Portfolio")
        
        portfolios = manager.list_portfolios()
        
        if not portfolios:
            st.info("No portfolios available. Create one first!")
        else:
            selected_portfolio_name = st.selectbox(
                "Select Portfolio to Edit",
                options=[p.name for p in portfolios],
                key="edit_portfolio_select"
            )
            
            if selected_portfolio_name:
                portfolio = manager.get_portfolio(selected_portfolio_name)
                
                # Portfolio info editing
                with st.form("edit_portfolio_info"):
                    st.write("**Portfolio Information**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_description = st.text_area(
                            "Description",
                            value=portfolio.description,
                            height=100
                        )
                        
                    with col2:
                        new_strategy = st.selectbox(
                            "Strategy",
                            options=[StrategyType.CONSERVATIVE, StrategyType.BALANCED, StrategyType.AGGRESSIVE, StrategyType.CUSTOM],
                            index=[StrategyType.CONSERVATIVE, StrategyType.BALANCED, StrategyType.AGGRESSIVE, StrategyType.CUSTOM].index(portfolio.strategy_type),
                            format_func=lambda x: x.value.title()
                        )
                    
                    update_info = st.form_submit_button("Update Portfolio Info")
                    
                    if update_info:
                        try:
                            manager.update_portfolio(
                                selected_portfolio_name,
                                description=new_description,
                                strategy_type=new_strategy
                            )
                            st.success("✅ Portfolio information updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating portfolio: {e}")
                
                # Stock management
                st.write("**Manage Holdings**")
                
                # Add new stock
                st.write("**Add New Stock**")
                
                # Use dynamic stock selector
                selected_symbol, stock_info = create_dynamic_stock_selector(
                    key=f"add_stock_{selected_portfolio_name}",
                    placeholder="Search stock symbol or company name... (e.g. AAPL, Apple)",
                    help_text="Enter stock symbol or company name for real-time search"
                )
                
                # If stock is selected, show weight settings and add button
                if selected_symbol and stock_info:
                    st.markdown("---")
                    
                    with st.form(f"add_stock_form_{selected_symbol}"):
                        st.markdown(f"### 🎯 Add **{selected_symbol}** to Portfolio")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            weight = st.number_input(
                                "Weight (%)", 
                                min_value=0.1, 
                                max_value=100.0, 
                                value=10.0, 
                                step=0.1,
                                help="Weight percentage of this stock in the portfolio"
                            )
                        
                        with col2:
                            target_weight = st.number_input(
                                "Target Weight (%)", 
                                min_value=0.1, 
                                max_value=100.0, 
                                value=weight, 
                                step=0.1,
                                help="Ideal target weight (optional)"
                            )
                        
                        notes = st.text_area(
                            "Investment Notes (optional)", 
                            placeholder="Record investment rationale or analysis...",
                            help="You can record reasons for selecting this stock"
                        )
                        
                        # Display current stock price information
                        if stock_info.get("current_price"):
                            st.info(f"💰 Current Price: ${stock_info['current_price']:.2f} | "
                                   f"📊 Weight: {weight}% | "
                                   f"🏢 Sector: {stock_info.get('sector', 'Unknown')}")
                        
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col2:
                            add_stock_submit = st.form_submit_button(
                                f"✅ Add {selected_symbol}", 
                                help=f"Add {selected_symbol} to portfolio",
                                use_container_width=True
                            )
                        
                        if add_stock_submit:
                            try:
                                # Save stock information to cache (prepare for future K-line and other features)
                                if 'portfolio_stock_cache' not in st.session_state:
                                    st.session_state.portfolio_stock_cache = {}
                                st.session_state.portfolio_stock_cache[selected_symbol] = stock_info
                                
                                # Add stock to portfolio
                                manager.add_stock(
                                    selected_portfolio_name,
                                    selected_symbol,
                                    weight / 100,
                                    target_weight=target_weight / 100 if target_weight != weight else None,
                                    notes=notes if notes else None
                                )
                                
                                st.success(f"🎉 Successfully added {selected_symbol} ({stock_info['name']}) to portfolio!")
                                st.balloons()  # Add some celebration effects
                                
                                # Clean selection state, prepare to add next stock
                                if f"add_stock_{selected_portfolio_name}_selected" in st.session_state:
                                    del st.session_state[f"add_stock_{selected_portfolio_name}_selected"]
                                
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error adding stock: {e}")
                else:
                    st.info("👆 Please search and select a stock to add first")
                
                # Current holdings
                if portfolio.holdings:
                    st.write("**Current Holdings**")
                    
                    # Create extended holdings data with cached stock information
                    holdings_data = []
                    for holding in portfolio.holdings:
                        deviation = holding.get_weight_deviation()
                        
                        # Get stock information from cache
                        stock_info = st.session_state.portfolio_stock_cache.get(holding.symbol)
                        current_price = stock_info.get('current_price') if stock_info else None
                        company_name = stock_info.get('name', holding.symbol) if stock_info else holding.symbol
                        sector = stock_info.get('sector', 'Unknown') if stock_info else 'Unknown'
                        
                        holdings_data.append({
                            'Symbol': holding.symbol,
                            'Company': company_name,
                            'Sector': sector,
                            'Current Price': f"${current_price:.2f}" if current_price else "N/A",
                            'Weight': f"{holding.weight:.1%}",
                            'Target Weight': f"{holding.target_weight:.1%}" if holding.target_weight else "N/A",
                            'Deviation': f"{deviation:+.1%}" if deviation else "N/A",
                            'Notes': holding.notes or ""
                        })
                    
                    df_holdings = pd.DataFrame(holdings_data)
                    st.dataframe(df_holdings, use_container_width=True)
                    
                    # Stock detailed information display
                    st.write("**📊 Detailed Portfolio Information**")
                    
                    # Create expandable stock information cards
                    for holding in portfolio.holdings:
                        expander_label = f"📈 {holding.symbol} Details"
                        with st.expander(expander_label):
                            stock_info = st.session_state.portfolio_stock_cache.get(holding.symbol)
                            if not stock_info:
                                with st.spinner(f"Getting {holding.symbol} information..."):
                                    stock_manager = get_stock_manager()
                                    stock_info = stock_manager.get_stock_info(holding.symbol)
                                    if stock_info:
                                        st.session_state.portfolio_stock_cache[holding.symbol] = stock_info
                                    else:
                                        st.error(f"Unable to retrieve {holding.symbol} information")
                                        return
                            if stock_info:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Current Price", f"${stock_info['current_price']:.2f}" if stock_info.get('current_price') else "N/A")
                                    st.write(f"**Sector**: {stock_info.get('sector', 'Unknown')}")
                                    st.write(f"**Industry**: {stock_info.get('industry', 'Unknown')}")
                                with col2:
                                    if stock_info.get('market_cap'):
                                        market_cap_b = stock_info['market_cap'] / 1e9
                                        st.metric("Market Cap", f"${market_cap_b:.1f}B")
                                    if stock_info.get('pe_ratio'):
                                        st.metric("P/E Ratio", f"{stock_info['pe_ratio']:.2f}")
                                with col3:
                                    if stock_info.get('dividend_yield'):
                                        dividend_pct = stock_info['dividend_yield'] * 100
                                        st.metric("Dividend Yield", f"{dividend_pct:.2f}%")
                                    if stock_info.get('beta'):
                                        st.metric("Beta Coefficient", f"{stock_info['beta']:.2f}")
                                if stock_info.get('description'):
                                    st.write("**Company Description**:")
                                    st.write(stock_info['description'])
                                st.info("💡 K-line chart feature will be added in future versions")
                    
                    st.markdown("---")
                    
                    # Remove stock functionality
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        stock_to_remove = st.selectbox(
                            "Select stock to remove",
                            options=[h.symbol for h in portfolio.holdings],
                            key="remove_stock_select"
                        )
                    
                    with col2:
                        st.write("")  # Spacing
                        if st.button("Remove Stock", type="secondary"):
                            try:
                                manager.remove_stock(selected_portfolio_name, stock_to_remove)
                                st.success(f"✅ Removed {stock_to_remove} from portfolio!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error removing stock: {e}")
                
                # Quick delete option at bottom
                st.divider()
                st.subheader("🗑️ Quick Delete")
                st.caption("Delete this entire portfolio")
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button("Delete Portfolio", type="secondary", use_container_width=True):
                        st.session_state.show_delete_confirm = True
                
                with col2:
                    if hasattr(st.session_state, 'show_delete_confirm') and st.session_state.show_delete_confirm:
                        if st.button("✅ Confirm Delete", type="primary"):
                            try:
                                success = manager.delete_portfolio(selected_portfolio_name)
                                if success:
                                    st.success(f"✅ Portfolio '{selected_portfolio_name}' deleted!")
                                    st.session_state.show_delete_confirm = False
                                    st.session_state.pop("edit_portfolio_select", None)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete portfolio")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                        
                        if st.button("❌ Cancel"):
                            st.session_state.show_delete_confirm = False
                            st.rerun()
    
    with tab3:
        st.subheader("Portfolio Details")
        
        portfolios = manager.list_portfolios()
        
        if not portfolios:
            st.info("No portfolios available.")
        else:
            selected_portfolio_name = st.selectbox(
                "Select Portfolio",
                options=[p.name for p in portfolios],
                key="details_portfolio_select"
            )
            
            if selected_portfolio_name:
                portfolio = manager.get_portfolio(selected_portfolio_name)
                
                # Basic info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Strategy", portfolio.strategy_type.value.title())
                
                with col2:
                    st.metric("Holdings", len(portfolio.holdings))
                
                with col3:
                    st.metric("Total Weight", f"{portfolio.total_weight:.1%}")
                
                # Description
                if portfolio.description:
                    st.write("**Description:**", portfolio.description)
                
                # Holdings visualization
                if portfolio.holdings:
                    fig = create_portfolio_overview_chart(portfolio)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Current vs target weights
                    if any(h.target_weight for h in portfolio.holdings):
                        fig_comparison = create_holdings_comparison_chart(portfolio)
                        if fig_comparison:
                            st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Rebalancing section
                st.subheader("⚖️ Portfolio Rebalancing")
                
                # Check if rebalancing is needed
                needs_rebalancing = False
                for holding in portfolio.holdings:
                    deviation = holding.get_weight_deviation()
                    if deviation and abs(deviation) > 0.05:  # 5% threshold
                        needs_rebalancing = True
                        break
                
                if needs_rebalancing:
                    st.warning("⚠️ Portfolio may need rebalancing")
                    
                    if st.button("Rebalance to Targets", type="primary"):
                        try:
                            rebalanced_portfolio = manager.rebalance_portfolio(selected_portfolio_name, method='target')
                            st.success("✅ Portfolio rebalanced successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error rebalancing portfolio: {e}")
                else:
                    st.success("✅ Portfolio is properly balanced")
                
                # Danger zone - Delete portfolio
                st.subheader("⚠️ Danger Zone")
                with st.expander("Delete Portfolio", expanded=False):
                    st.error("**Warning**: This action cannot be undone!")
                    st.write(f"Are you sure you want to delete portfolio **'{selected_portfolio_name}'**?")
                    
                    # Confirmation input
                    confirmation = st.text_input(
                        f"Type '{selected_portfolio_name}' to confirm deletion:",
                        key="delete_confirmation"
                    )
                    
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if st.button(
                            "🗑️ DELETE", 
                            type="secondary", 
                            disabled=(confirmation != selected_portfolio_name),
                            key="confirm_delete"
                        ):
                            try:
                                success = manager.delete_portfolio(selected_portfolio_name)
                                if success:
                                    st.success(f"✅ Portfolio '{selected_portfolio_name}' deleted successfully!")
                                    st.balloons()
                                    # Clear the selectbox to avoid errors
                                    st.session_state.pop("details_portfolio_select", None)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete portfolio")
                            except Exception as e:
                                st.error(f"❌ Error deleting portfolio: {e}")
                    
                    with col2:
                        if confirmation and confirmation != selected_portfolio_name:
                            st.warning("⚠️ Portfolio name doesn't match. Please type the exact name.")


def show_portfolio_analysis():
    """Show portfolio analysis page."""
    st.markdown('<h1 class="main-header">🔍 Portfolio Analysis</h1>', unsafe_allow_html=True)
    
    manager = st.session_state.portfolio_manager
    analyzer = st.session_state.portfolio_analyzer
    
    portfolios = manager.list_portfolios()
    
    if not portfolios:
        st.info("No portfolios available for analysis. Create one first!")
        return
    
    # Portfolio selection
    selected_portfolio_name = st.selectbox(
        "Select Portfolio to Analyze",
        options=[p.name for p in portfolios]
    )
    
    if not selected_portfolio_name:
        return
    
    portfolio = manager.get_portfolio(selected_portfolio_name)
    
    # Analysis options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Analysis for: {portfolio.name}")
    
    with col2:
        force_refresh = st.checkbox("Force Refresh", help="Ignore cached analysis")
    
    # Perform analysis
    try:
        with st.spinner("Analyzing portfolio..."):
            analysis = analyzer.analyze_portfolio(portfolio, force_refresh=force_refresh)
        
        # Overall recommendation
        st.subheader("💡 Overall Recommendation")
        
        overall = analysis['overall_recommendation']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Recommendation", overall['strength'])
        
        with col2:
            confidence_color = "normal" if overall['confidence'] > 0.7 else "inverse"
            st.metric("Confidence", f"{overall['confidence']:.1%}")
        
        with col3:
            st.write("**Reason:**")
            st.write(overall['reason'])
        
        # Key metrics
        st.subheader("📊 Key Metrics")
        
        metrics = analysis['portfolio_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Expected Return", f"{metrics['expected_return']:.1%}")
        
        with col2:
            risk_score = metrics['risk_score']
            risk_delta = None
            if risk_score > 0.7:
                risk_delta = "High"
            elif risk_score < 0.3:
                risk_delta = "Low"
            st.metric("Risk Score", f"{risk_score:.2f}", delta=risk_delta)
        
        with col3:
            st.metric("Diversification", f"{metrics['diversification_score']:.1%}")
        
        with col4:
            st.metric("Largest Position", f"{metrics['largest_position']:.1%}")
        
        # Portfolio holdings overview
        st.subheader("📋 Portfolio Holdings")
        
        individual = analysis['individual_analysis']
        
        # Create a simple holdings table
        holdings_data = []
        for symbol, stock_analysis in individual.items():
            holdings_data.append({
                'Symbol': symbol,
                'Weight': f"{stock_analysis['weight']:.1%}",
                'Recommendation': stock_analysis['recommendation'],
                'Confidence': f"{stock_analysis['confidence']:.1%}",
                'Risk Score': f"{stock_analysis['risk_score']:.2f}",
                'Current Price': f"${stock_analysis.get('current_price', 0):.2f}" if stock_analysis.get('current_price') else "N/A"
            })
        
        if holdings_data:
            df_holdings = pd.DataFrame(holdings_data)
            st.dataframe(df_holdings, use_container_width=True)
        
        # Risk assessment
        st.subheader("⚠️ Risk Assessment")
        
        risk = analysis['risk_assessment']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Risk Level:** {risk['risk_level']}")
            st.markdown(f"**Risk Score:** {risk['risk_score']:.2f}")
            st.markdown(f"**Concentration Risk:** {risk['concentration_risk']:.1%}")
        
        with col2:
            if risk['risk_factors']:
                st.markdown("**Risk Factors:**")
                for factor in risk['risk_factors']:
                    st.markdown(f"• {factor}")
            else:
                st.success("✅ No significant risk factors identified")
        
        # Rebalancing suggestions
        st.subheader("⚖️ Rebalancing Suggestions")
        
        rebalance_suggestions = analysis.get('rebalance_suggestions', [])
        
        if rebalance_suggestions:
            suggestion_data = []
            for suggestion in rebalance_suggestions:
                if 'symbol' in suggestion:
                    suggestion_data.append({
                        'Stock': suggestion['symbol'],
                        'Action': suggestion['action'].title(),
                        'Current Weight': f"{suggestion['current_weight']:.1%}",
                        'Target Weight': f"{suggestion['target_weight']:.1%}",
                        'Deviation': f"{suggestion['deviation']:+.1%}",
                        'Priority': suggestion['priority'].title()
                    })
            
            if suggestion_data:
                df_suggestions = pd.DataFrame(suggestion_data)
                st.dataframe(df_suggestions, use_container_width=True)
            
            # Rebalance button
            if st.button("Apply Rebalancing", type="primary"):
                try:
                    manager.rebalance_portfolio(portfolio.name, method='target')
                    st.success("✅ Portfolio rebalanced successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error rebalancing: {e}")
        else:
            st.success("✅ No rebalancing needed - portfolio is well balanced")
        
        # Diversification analysis
        st.subheader("🌐 Diversification Analysis")
        
        diversification = analysis['diversification_analysis']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Diversification Score", f"{diversification['diversification_score']:.1%}")
            st.metric("Holdings Count", diversification['holdings_count'])
            st.metric("Concentration Risk", f"{diversification['concentration_risk']:.1%}")
        
        with col2:
            # Sector breakdown
            sectors = diversification['sector_analysis']
            sector_data = {k: v for k, v in sectors.items() if v > 0}
            
            if sector_data:
                st.markdown("**Sector Breakdown:**")
                for sector, weight in sector_data.items():
                    st.markdown(f"• {sector}: {weight:.1%}")
        
        # Diversification recommendations
        if diversification['recommendations']:
            st.markdown("**Diversification Recommendations:**")
            for rec in diversification['recommendations']:
                st.markdown(f"• {rec}")
        
        # Analysis cache info
        if analysis.get('is_cached'):
            st.info("ℹ️ This analysis used cached data. Check 'Force Refresh' for updated analysis.")
        
        # Automated Trading section (moved to bottom of page)
        st.markdown("---")
        st.header("🚀 Automated Trading")
        
        # Automated Trading option
        enable_auto_trading = st.checkbox(
            "Enable Automated Trading",
            help="Automatically generate and execute trading recommendations for this portfolio"
        )
        
        # Trading configuration (only show if automated trading is enabled)
        if enable_auto_trading:
            st.markdown("### ⚙️ Trading Configuration")
            
            # Check if simulation components are available
            if not SIMULATION_AVAILABLE:
                st.error("❌ Simulation trading components are not available")
                enable_auto_trading = False
            else:
                # Select account
                user_id = "demo_user"
                accounts = st.session_state.simulation_manager.get_user_accounts(user_id)
                
                if not accounts:
                    st.warning("No simulation accounts available. Create an account in Simulation > Account Management first.")
                    enable_auto_trading = False
                else:
                    account_id = st.selectbox(
                        "Select Trading Account",
                        [acc.account_id for acc in accounts],
                        format_func=lambda x: next(acc.account_name for acc in accounts if acc.account_id == x),
                        key="analysis_auto_trade_account"
                    )
                    
                    account = next(acc for acc in accounts if acc.account_id == account_id)
                    
                    # Display account status
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Available Funds", f"${account.available_balance:,.0f}")
                    with col2:
                        st.metric("Total Assets", f"${account.total_value:,.0f}")
                    with col3:
                        st.metric("Return Rate", f"{account.total_return:+.1f}%")
                    
                    # Trading configuration
                    trade_col1, trade_col2, trade_col3 = st.columns(3)
                    
                    with trade_col1:
                        investment_amount = st.number_input(
                            "Investment Amount ($)",
                            min_value=100.0,
                            max_value=float(account.available_balance),
                            value=min(10000.0, float(account.available_balance)),
                            step=100.0,
                            key="analysis_auto_trade_amount"
                        )
                    
                    with trade_col2:
                        risk_level = st.selectbox(
                            "Risk Level",
                            ["conservative", "moderate", "aggressive"],
                            format_func=lambda x: {
                                "conservative": "Conservative (Low Risk)",
                                "moderate": "Moderate (Balanced)",
                                "aggressive": "Aggressive (High Risk)"
                            }.get(x, x),
                            key="analysis_auto_trade_risk"
                        )
                    
                    with trade_col3:
                        analysis_method = st.selectbox(
                            "Analysis Method",
                            ["comprehensive", "technical", "fundamental"],
                            format_func=lambda x: {
                                "comprehensive": "Comprehensive",
                                "technical": "Technical Only",
                                "fundamental": "Fundamental Only"
                            }.get(x, x),
                            key="analysis_auto_trade_analysis"
                        )
            
            # Automated Trading execution (only show if enabled)
            if enable_auto_trading and SIMULATION_AVAILABLE and 'account' in locals():
                st.markdown("### 🚀 Execute Trading")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("**Ready to execute automated trading based on the analysis above.**")
                    st.markdown(f"• **Portfolio:** {portfolio.name} ({len(portfolio.holdings)} stocks)")
                    st.markdown(f"• **Investment:** ${investment_amount:,.0f}")
                    st.markdown(f"• **Risk Level:** {risk_level.title()}")
                    st.markdown(f"• **Analysis Method:** {analysis_method.title()}")
                
                with col2:
                    execute_trading = st.button(
                        "🚀 Execute Automated Trading",
                        type="primary",
                        key="execute_analysis_auto_trade",
                        help="Execute automated trading based on portfolio analysis"
                    )
                
                if execute_trading:
                    selected_stocks = [h.symbol for h in portfolio.holdings]
                    
                    with st.spinner("🤖 Analyzing stocks and generating recommendations..."):
                        try:
                            # Import required components
                            from src.engines.recommendation_engine import RecommendationEngine
                            from src.analyzers.stock_analyzer import StockAnalyzer
                            from src.languages.config import LanguageConfig
                            
                            # Map analysis method to strategy type
                            strategy_mapping = {
                                "comprehensive": "all",
                                "technical": "technical",
                                "fundamental": "quantitative"
                            }
                            strategy_type = strategy_mapping.get(analysis_method, "all")
                            
                            # Generate recommendations
                            recommendations = []
                            lang_config = LanguageConfig("en")
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i, symbol in enumerate(selected_stocks):
                                try:
                                    status_text.text(f"🔍 Analyzing {symbol}...")
                                    progress_bar.progress((i) / len(selected_stocks))
                                    
                                    # Create analyzer
                                    analyzer_instance = StockAnalyzer(symbol)
                                    analyzer_instance.fetch_data()
                                    
                                    # Generate recommendation
                                    recommendation_engine = RecommendationEngine(analyzer_instance, lang_config)
                                    recommendation = recommendation_engine.generate_recommendation_for_symbol(
                                        analyzer_instance, symbol, strategy_type
                                    )
                                    
                                    recommendations.append(recommendation)
                                    
                                except Exception as e:
                                    st.warning(f"⚠️ Failed to analyze {symbol}: {str(e)}")
                                    continue
                            
                            progress_bar.progress(1.0)
                            status_text.text("✅ Analysis completed!")
                            
                            if not recommendations:
                                st.error("❌ No valid recommendations generated")
                                return
                            
                            # Execute automated trading
                            status_text.text("💰 Executing automated trades...")
                            result = st.session_state.automated_trader.execute_portfolio_recommendations(
                                account.account_id,
                                recommendations,
                                available_cash=investment_amount
                            )
                            
                            if result["success"]:
                                st.success("✅ Automated trading completed successfully!")
                                
                                # Display results
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Successful Trades", result["successful_trades"])
                                with col2:
                                    st.metric("Failed Trades", result["failed_trades_count"])
                                with col3:
                                    st.metric("Total Invested", f"${result['total_invested']:,.0f}")
                                with col4:
                                    st.metric("Recommendations", len(recommendations))
                                
                                # Show recommendation breakdown
                                if "recommendation_summary" in result:
                                    rec_summary = result["recommendation_summary"]
                                    st.markdown("**Recommendation Breakdown:**")
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.info(f"🟢 BUY: {rec_summary['buy_recommendations']}")
                                    with col2:
                                        st.info(f"🔴 SELL: {rec_summary['sell_recommendations']}")
                                    with col3:
                                        st.info(f"🟡 HOLD: {rec_summary['hold_recommendations']}")
                                    
                                    # Explain if no trades were executed
                                    if result["successful_trades"] == 0 and result["failed_trades_count"] == 0:
                                        if rec_summary['buy_recommendations'] == 0 and rec_summary['sell_recommendations'] == 0:
                                            st.warning("⚠️ No BUY or SELL recommendations were generated. All recommendations were HOLD. Consider using different stocks or analysis methods to generate trading signals.")
                                
                                # Account status update
                                if result["account_summary"]:
                                    acc = result["account_summary"]["account"]
                                    st.markdown("### 📊 Account Status Update")
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Current Balance", f"${acc.current_balance:,.2f}")
                                    with col2:
                                        st.metric("Total Value", f"${acc.total_value:,.2f}")
                                    with col3:
                                        st.metric("Total Return", f"{acc.total_return:+.1f}%")
                                
                                # Portfolio holdings update
                                st.markdown("### 📁 Portfolio Holdings Update")
                                try:
                                    # Get account positions from trading results
                                    account_summary = result.get("account_summary", {})
                                    positions = account_summary.get("positions", {})
                                    
                                    if positions:
                                        # Portfolio summary
                                        total_value = sum(pos.market_value for pos in positions.values())
                                        total_positions = len(positions)
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            st.metric("Total Positions", total_positions)
                                        with col2:
                                            st.metric("Portfolio Value", f"${total_value:,.2f}")
                                        with col3:
                                            st.metric("Account", account.account_name)
                                        with col4:
                                            st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))
                                        
                                        # Holdings table
                                        st.markdown("**Current Positions:**")
                                        
                                        holdings_data = []
                                        for symbol, position in positions.items():
                                            holdings_data.append({
                                                "Symbol": symbol,
                                                "Quantity": f"{position.quantity:,.0f}",
                                                "Avg Cost": f"${position.average_cost:.2f}",
                                                "Current Price": f"${position.current_price:.2f}",
                                                "Market Value": f"${position.market_value:,.2f}",
                                                "Unrealized P&L": f"${position.unrealized_pnl:+,.2f}",
                                                "P&L %": f"{position.unrealized_pnl_pct:+.1f}%"
                                            })
                                        
                                        holdings_df = pd.DataFrame(holdings_data)
                                        st.dataframe(holdings_df, use_container_width=True)
                                        
                                        # Holdings summary
                                        st.markdown("**Portfolio Summary:**")
                                        total_cost = sum(pos.average_cost * pos.quantity for pos in positions.values())
                                        total_pnl = sum(pos.unrealized_pnl for pos in positions.values())
                                        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
                                        
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Total Cost Basis", f"${total_cost:,.2f}")
                                        with col2:
                                            st.metric("Total P&L", f"${total_pnl:+,.2f}")
                                        with col3:
                                            st.metric("Total P&L %", f"{total_pnl_pct:+.1f}%")
                                    else:
                                        st.info("No positions in account after trading.")
                                        
                                except Exception as e:
                                    st.warning(f"⚠️ Could not refresh account positions: {e}")
                                    # Fallback to portfolio holdings if account positions unavailable
                                    try:
                                        updated_portfolio = manager.get_portfolio(portfolio.name)
                                        if updated_portfolio.holdings:
                                            st.markdown("**Portfolio Holdings (from portfolio data):**")
                                            holdings_text = ", ".join([f"{h.symbol} ({h.weight:.1f}%)" for h in updated_portfolio.holdings])
                                            st.info(holdings_text)
                                    except Exception as e2:
                                        st.warning(f"⚠️ Could not load portfolio data either: {e2}")
                                
                                # Executed trade details
                                if result["executed_trades"]:
                                    st.markdown("### 💼 Executed Trades")
                                    for trade in result["executed_trades"]:
                                        with st.expander(f"{trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}"):
                                            st.write(f"Amount: ${trade['amount']:,.2f}")
                                            if 'recommendation' in trade:
                                                rec = trade['recommendation']['recommendation']
                                                st.write(f"AI Recommendation: {rec['action']} (confidence: {rec['confidence']})")
                                
                                # Failed trades
                                if result["failed_trades"]:
                                    st.markdown("### ❌ Failed Trades")
                                    for trade in result["failed_trades"]:
                                        st.error(f"{trade['action']} {trade['symbol']}: {trade['error']}")
                            
                            else:
                                st.error(f"❌ Automated trading failed: {result.get('error', 'Unknown error')}")
                            
                        except Exception as e:
                            st.error(f"❌ Error during automated trading: {str(e)}")
                        finally:
                            progress_bar.empty()
                            status_text.empty()
    
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")


def show_portfolio_comparison():
    """Show portfolio comparison page."""
    st.markdown('<h1 class="main-header">🆚 Portfolio Comparison</h1>', unsafe_allow_html=True)
    
    manager = st.session_state.portfolio_manager
    analyzer = st.session_state.portfolio_analyzer
    
    portfolios = manager.list_portfolios()
    
    if len(portfolios) < 2:
        st.warning("⚠️ Need at least 2 portfolios for comparison. Create more portfolios first!")
        return
    
    # Portfolio selection
    col1, col2 = st.columns(2)
    
    with col1:
        portfolio1_name = st.selectbox(
            "Select First Portfolio",
            options=[p.name for p in portfolios],
            key="compare_portfolio1"
        )
    
    with col2:
        portfolio2_name = st.selectbox(
            "Select Second Portfolio", 
            options=[p.name for p in portfolios if p.name != portfolio1_name],
            key="compare_portfolio2"
        )
    
    if not (portfolio1_name and portfolio2_name):
        return
    
    # Get portfolios
    portfolio1 = manager.get_portfolio(portfolio1_name)
    portfolio2 = manager.get_portfolio(portfolio2_name)
    
    # Perform comparison
    try:
        with st.spinner("Comparing portfolios..."):
            comparison = analyzer.compare_portfolios(portfolio1, portfolio2)
        
        # Comparison header
        st.subheader(f"🔄 Comparing: {portfolio1_name} vs {portfolio2_name}")
        
        # Basic info comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{portfolio1_name}**")
            st.markdown(f"• Strategy: {portfolio1.strategy_type.value.title()}")
            st.markdown(f"• Holdings: {len(portfolio1.holdings)}")
            st.markdown(f"• Total Weight: {portfolio1.total_weight:.1%}")
        
        with col2:
            st.markdown(f"**{portfolio2_name}**")
            st.markdown(f"• Strategy: {portfolio2.strategy_type.value.title()}")
            st.markdown(f"• Holdings: {len(portfolio2.holdings)}")
            st.markdown(f"• Total Weight: {portfolio2.total_weight:.1%}")
        
        # Performance comparison
        st.subheader("📊 Performance Comparison")
        
        comp_metrics = comparison['comparison']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            return_diff = comp_metrics['expected_return_diff']
            st.metric(
                "Return Difference",
                f"{return_diff:+.1%}",
                delta=f"Portfolio 1 {'higher' if return_diff > 0 else 'lower'}"
            )
        
        with col2:
            risk_diff = comp_metrics['risk_diff']
            st.metric(
                "Risk Difference", 
                f"{risk_diff:+.2f}",
                delta=f"Portfolio 1 {'riskier' if risk_diff > 0 else 'safer'}"
            )
        
        with col3:
            div_diff = comp_metrics['diversification_diff']
            st.metric(
                "Diversification Difference",
                f"{div_diff:+.1%}",
                delta=f"Portfolio 1 {'better' if div_diff > 0 else 'worse'}"
            )
        
        with col4:
            conf_diff = comp_metrics['confidence_diff']
            st.metric(
                "Confidence Difference",
                f"{conf_diff:+.1%}",
                delta=f"Portfolio 1 {'higher' if conf_diff > 0 else 'lower'}"
            )
        
        # Overall recommendation
        st.subheader("💡 Comparison Result")
        st.markdown(f"**Recommendation:** {comparison['recommendation']}")
        
        # Detailed analysis comparison
        st.subheader("📈 Detailed Analysis Comparison")
        
        analysis1 = comparison['portfolio1']['analysis']
        analysis2 = comparison['portfolio2']['analysis']
        
        # Create comparison table
        comparison_data = []
        
        metrics_to_compare = [
            ('Expected Return', 'portfolio_metrics', 'expected_return', ':.1%'),
            ('Risk Score', 'portfolio_metrics', 'risk_score', ':.2f'),
            ('Diversification', 'portfolio_metrics', 'diversification_score', ':.1%'),
            ('Risk Level', 'risk_assessment', 'risk_level', ''),
            ('Recommendation', 'overall_recommendation', 'recommendation', ''),
            ('Confidence', 'overall_recommendation', 'confidence', ':.1%')
        ]
        
        for metric_name, category, key, format_str in metrics_to_compare:
            value1 = analysis1[category][key]
            value2 = analysis2[category][key]
            
            if format_str:
                # Handle None values and ensure proper numeric formatting
                try:
                    if value1 is not None and isinstance(value1, (int, float)):
                        if format_str == ':.1%':
                            value1_str = f"{value1:.1%}"
                        elif format_str == ':.2f':
                            value1_str = f"{value1:.2f}"
                        else:
                            value1_str = format(value1, format_str.lstrip(':'))
                    else:
                        value1_str = "N/A"
                except (ValueError, TypeError):
                    value1_str = "N/A"
                
                try:
                    if value2 is not None and isinstance(value2, (int, float)):
                        if format_str == ':.1%':
                            value2_str = f"{value2:.1%}"
                        elif format_str == ':.2f':
                            value2_str = f"{value2:.2f}"
                        else:
                            value2_str = format(value2, format_str.lstrip(':'))
                    else:
                        value2_str = "N/A"
                except (ValueError, TypeError):
                    value2_str = "N/A"
            else:
                value1_str = str(value1) if value1 is not None else "N/A"
                value2_str = str(value2) if value2 is not None else "N/A"
            
            comparison_data.append({
                'Metric': metric_name,
                portfolio1_name: value1_str,
                portfolio2_name: value2_str
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
        
        # Risk-return visualization
        st.subheader("📊 Risk-Return Visualization")
        
        analyses = [analysis1, analysis2]
        fig = create_risk_return_chart(analyses)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Comparison failed: {e}")


def show_settings():
    """Show settings and configuration page."""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    # Language settings
    st.subheader("🌐 Language Settings")
    
    current_language = getattr(st.session_state.portfolio_analyzer, 'language', 'en')
    
    new_language = st.selectbox(
        "Analysis Language",
        options=['en', 'zh'],
        index=0 if current_language == 'en' else 1,
        format_func=lambda x: 'English' if x == 'en' else 'Chinese'
    )
    
    if new_language != current_language:
        st.session_state.portfolio_analyzer = PortfolioAnalyzer(language=new_language)
        st.success(f"✅ Language changed to {'English' if new_language == 'en' else 'Chinese'}")
        st.rerun()
    
    # Data management
    st.subheader("💾 Data Management")
    
    manager = st.session_state.portfolio_manager
    portfolios = manager.list_portfolios()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Portfolio Statistics:**")
        st.markdown(f"• Total Portfolios: {len(portfolios)}")
        st.markdown(f"• Total Holdings: {sum(len(p.holdings) for p in portfolios)}")
        
        # Storage info
        portfolio_dir = os.path.expanduser("~/.stock_recommender/portfolios")
        if os.path.exists(portfolio_dir):
            json_files = [f for f in os.listdir(portfolio_dir) if f.endswith('.json')]
            st.markdown(f"• Saved Files: {len(json_files)}")
    
    with col2:
        st.markdown("**Actions:**")
        
        if st.button("Clear Analysis Cache"):
            st.session_state.analysis_cache = {}
            st.success("✅ Analysis cache cleared")
        
        if portfolios and st.button("Export All Portfolios"):
            try:
                # This would implement export functionality
                st.info("📋 Export functionality would be implemented here")
            except Exception as e:
                st.error(f"❌ Export failed: {e}")
    
    # System information
    st.subheader("ℹ️ System Information")
    
    st.markdown("**Portfolio Management System**")
    st.markdown("• Version: 1.0.0")
    st.markdown("• Built with Streamlit")
    st.markdown("• Supports multiple portfolios and analysis")


# Simulation Trading Functions
def show_simulation_unavailable():
    """Display simulation trading unavailable page"""
    st.header("🎮 Simulation Trading")
    st.warning("⚠️ Simulation features are not available")
    st.info("Simulation components could not be loaded properly. Please check system configuration.")
    st.markdown("""
    **Possible causes:**
    - Simulation modules failed to import
    - Missing dependencies
    - System configuration issues
    """)

def show_simulation():
    """Display simulation trading main page"""
    st.header("🎮 Simulation Trading")

    # Get simulation trading manager
    simulation_manager = st.session_state.simulation_manager
    virtual_trader = st.session_state.virtual_trader
    backtest_engine = st.session_state.backtest_engine
    
    # Subpage navigation
    simulation_pages = {
        "Account Management": show_simulation_accounts,
        "Virtual Trading": show_virtual_trading,
        "Automated Trading": show_automated_trading,
        "Historical Backtesting": show_backtesting,
        "Performance Analysis": show_performance_analysis
    }
    
    selected_simulation_page = st.sidebar.selectbox(
        "Simulation Features",
        options=list(simulation_pages.keys()),
        key="simulation_page"
    )
    
    # Execute selected subpage
    simulation_pages[selected_simulation_page]()

def show_simulation_accounts():
    """Display simulation account management page"""
    st.subheader("🎮 Simulation Accounts")
    
    simulation_manager = st.session_state.simulation_manager
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### My Accounts")
        
        # Get user accounts (using user ID from session or default value)
        user_id = st.session_state.get('user_id', 'demo_user')
        accounts = simulation_manager.get_user_accounts(user_id)
        
        if not accounts:
            st.info("You don't have any simulation accounts yet. Create one to start investing!")
            with st.form("create_account_form"):
                account_name = st.text_input("Account Name", "My Simulation Account")
                initial_balance = st.number_input("Initial Balance", min_value=1000.0, value=100000.0, step=1000.0)
                
                if st.form_submit_button("Create Account", type="primary"):
                    try:
                        account = simulation_manager.create_account(
                            user_id=user_id,
                            account_name=account_name,
                            initial_balance=initial_balance
                        )
                        st.success(f"✅ Account created successfully! Initial balance: ${account.initial_balance:,.0f}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to create account: {str(e)}")
        else:
            for account in accounts:
                with st.expander(f"📊 {account.account_name}", expanded=True):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Total Value", f"${account.total_value:,.0f}")
                        st.metric("Available Balance", f"${account.available_balance:,.0f}")
                    
                    with col_b:
                        pnl = account.total_value - account.initial_balance
                        pnl_pct = account.total_return
                        st.metric("P&L", f"${pnl:+,.0f}",
                                delta=f"{pnl_pct:+.1f}%" if pnl_pct else None)
                    
                    with col_c:
                        positions = simulation_manager.calculate_positions(account.account_id)
                        st.metric("Positions", len(positions))
                        st.metric("Total Return", f"{account.total_return:+.1f}%")
    
    with col2:
        st.markdown("### Quick Actions")
        
        if accounts:
            if st.button("💰 Add Funds", type="secondary"):
                st.info("Add funds feature coming soon...")
            
            if st.button("📈 View Transaction History", type="secondary"):
                st.info("Transaction history view coming soon...")

def show_virtual_trading():
    """Display virtual trading page"""
    st.subheader("💹 Virtual Trading")
    
    simulation_manager = st.session_state.simulation_manager
    virtual_trader = st.session_state.virtual_trader
    
    # Select account
    user_id = st.session_state.get('user_id', 'demo_user')
    accounts = simulation_manager.get_user_accounts(user_id)
    
    if not accounts:
        st.warning("Please create a simulation account first")
        return
    
    account_id = st.selectbox(
        "Select Trading Account",
        [acc.account_id for acc in accounts],
        format_func=lambda x: next(acc.account_name for acc in accounts if acc.account_id == x)
    )
    
    account = next(acc for acc in accounts if acc.account_id == account_id)
    
    # Display account status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Available Balance", f"${account.available_balance:,.0f}")
    with col2:
        st.metric("Total Value", f"${account.total_value:,.0f}")
    with col3:
        st.metric("Total Return", f"{account.total_return:+.1f}%")
    
    st.markdown("---")
    
    # Trading form
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Buy Stocks")
        with st.form("buy_form"):
            buy_symbol = st.text_input("Stock Symbol", "AAPL").upper()
            buy_quantity = st.number_input("Quantity", min_value=1, value=10)
            
            buy_submitted = st.form_submit_button("Buy", type="primary")
            
            if buy_submitted:
                try:
                    # Execute trade
                    transaction = virtual_trader.execute_buy_order(
                        account_id, buy_symbol, buy_quantity
                    )
                    
                    st.success(f"✅ Buy successful!\\n"
                             f"Stock: {buy_symbol}\\n"
                             f"Quantity: {buy_quantity}\\n"
                             f"Price: ${transaction.price:.2f}\\n"
                             f"Total Amount: ${transaction.total_amount:.2f}")
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Trade failed: {str(e)}")
    
    with col2:
        st.markdown("### 📉 Sell Stocks")
        with st.form("sell_form"):
            # Get current positions
            positions = simulation_manager.calculate_positions(account_id)
            if positions:
                sell_symbol = st.selectbox("Select Stock", list(positions.keys()))
                max_quantity = positions[sell_symbol].quantity
                sell_quantity = st.number_input("Quantity", min_value=1, max_value=max_quantity, value=min(10, max_quantity))
                
                sell_submitted = st.form_submit_button("Sell", type="secondary")
                
                if sell_submitted:
                    try:
                        # Execute trade
                        transaction = virtual_trader.execute_sell_order(
                            account_id, sell_symbol, sell_quantity
                        )
                        
                        st.success(f"✅ Sell successful!\\n"
                                 f"Stock: {sell_symbol}\\n"
                                 f"Quantity: {sell_quantity}\\n"
                                 f"Price: ${transaction.price:.2f}\\n"
                                 f"Total Amount: ${transaction.total_amount:.2f}")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Trade failed: {str(e)}")
            else:
                st.info("No positions available")
    
    # Display current positions
    st.markdown("---")
    st.markdown("### 📊 Current Positions")
    
    positions = simulation_manager.calculate_positions(account_id)
    if positions:
        positions_data = []
        for symbol, position in positions.items():
            positions_data.append({
                "Stock": symbol,
                "Quantity": position.quantity,
                "Avg Cost": f"${position.average_cost:.2f}",
                "Current Price": f"${position.current_price:.2f}",
                "Market Value": f"${position.market_value:.2f}",
                "P&L": f"${position.unrealized_pnl:+.2f}",
                "P&L %": f"{position.unrealized_pnl_pct:+.1f}%"
            })
        
        st.dataframe(positions_data, use_container_width=True)
    else:
        st.info("No positions")
    
    # Sync to Portfolio section
    st.markdown("---")
    st.markdown("### 🔄 Sync to Portfolio")
    st.markdown("Sync your virtual trading positions to a real portfolio for performance analysis.")
    
    # Portfolio selection for sync
    portfolios = st.session_state.portfolio_manager.list_portfolios()
    
    if not portfolios:
        st.warning("No portfolios available. Create a portfolio first to sync positions.")
    else:
        portfolio_options = {p.name: f"{p.name} ({len(p.holdings)} stocks)" for p in portfolios}
        selected_portfolio_name = st.selectbox(
            "Select Portfolio to Sync To",
            options=list(portfolio_options.keys()),
            format_func=lambda x: portfolio_options[x],
            key="sync_portfolio_select"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔄 Sync Positions to Portfolio", type="primary"):
                try:
                    # Get current positions
                    current_positions = simulation_manager.calculate_positions(account_id)
                    
                    if not current_positions:
                        st.warning("No positions to sync. Make some virtual trades first.")
                        return
                    
                    # Sync positions to portfolio
                    success_count = 0
                    error_messages = []
                    
                    for symbol, position in current_positions.items():
                        try:
                            # Calculate weight based on position value relative to total portfolio value
                            position_value = position.market_value
                            total_portfolio_value = sum(p.market_value for p in current_positions.values())
                            weight = position_value / total_portfolio_value if total_portfolio_value > 0 else 0
                            
                            # Check if holding already exists
                            portfolio = st.session_state.portfolio_manager.get_portfolio(selected_portfolio_name)
                            existing_holding = portfolio.get_holding(symbol)
                            
                            if existing_holding:
                                # Update existing holding
                                st.session_state.portfolio_manager.update_stock_weight(
                                    selected_portfolio_name,
                                    symbol,
                                    weight
                                )
                                # Update notes separately
                                existing_holding.notes = f"Updated from virtual trading - {position.quantity} shares @ ${position.average_cost:.2f}"
                                existing_holding.last_updated = datetime.now()
                                # Save the portfolio after updating notes
                                st.session_state.portfolio_manager.file_manager.save_portfolio(portfolio)
                            else:
                                # Add new holding
                                st.session_state.portfolio_manager.add_stock(
                                    selected_portfolio_name,
                                    symbol,
                                    weight,
                                    notes=f"Synced from virtual trading - {position.quantity} shares @ ${position.average_cost:.2f}"
                                )
                            success_count += 1
                            
                        except Exception as e:
                            error_messages.append(f"Failed to sync {symbol}: {str(e)}")
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully synced {success_count} positions to portfolio '{selected_portfolio_name}'")
                        
                        # Show updated portfolio summary
                        updated_portfolio = st.session_state.portfolio_manager.get_portfolio(selected_portfolio_name)
                        st.info(f"Portfolio now has {len(updated_portfolio.holdings)} holdings")
                        
                        st.rerun()
                    
                    if error_messages:
                        for error in error_messages:
                            st.error(error)
                            
                except Exception as e:
                    st.error(f"❌ Sync failed: {str(e)}")
        
        with col2:
            if st.button("📊 View Synced Portfolio", type="secondary"):
                if selected_portfolio_name:
                    # Switch to portfolio analysis page
                    st.session_state.selected_page = "🔍 Portfolio Analysis"
                    st.session_state.analysis_portfolio = selected_portfolio_name
                    st.rerun()
                else:
                    st.warning("Please select a portfolio first.")

def show_backtesting():
    """Display historical backtesting page"""
    st.subheader("📈 Historical Backtesting")
    
    backtest_engine = st.session_state.backtest_engine
    
    with st.form("backtest_form"):
        st.markdown("### Backtest Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            symbols = st.multiselect(
                "Select Stocks",
                ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"],
                default=["AAPL", "MSFT"]
            )
            
            strategy = st.selectbox(
                "Investment Strategy",
                ["buy_and_hold", "mean_reversion"],
                format_func=lambda x: {
                    "buy_and_hold": "Buy and Hold",
                    "mean_reversion": "Mean Reversion"
                }.get(x, x)
            )
        
        with col2:
            start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
            end_date = st.date_input("End Date", value=pd.to_datetime("2023-12-31"))
            initial_balance = st.number_input("Initial Balance", min_value=1000, value=100000)
        
        submitted = st.form_submit_button("Run Backtest", type="primary")
        
        if submitted and symbols:
            with st.spinner("Running historical backtest..."):
                try:
                    result = backtest_engine.run_backtest(
                        strategy_config={"type": strategy},
                        symbols=symbols,
                        start_date=pd.to_datetime(start_date),
                        end_date=pd.to_datetime(end_date),
                        initial_balance=initial_balance
                    )
                    
                    if result.get("success"):
                        st.success("✅ Backtest completed!")
                        
                        # Display results
                        perf = result["performance"]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Return", f"{perf['total_return']:+.1f}%")
                        with col2:
                            st.metric("Annualized Return", f"{perf['annualized_return']:+.1f}%")
                        with col3:
                            st.metric("Max Drawdown", f"{perf['max_drawdown']:.1f}%")
                        with col4:
                            st.metric("Sharpe Ratio", f"{perf['sharpe_ratio']:.2f}")
                        
                        # Display portfolio value curve
                        portfolio_values = result["portfolio_values"]
                        if portfolio_values:
                            chart_data = pd.DataFrame(portfolio_values)
                            chart_data["date"] = pd.to_datetime(chart_data["date"])
                            
                            st.markdown("### 📊 Portfolio Value Chart")
                            st.line_chart(chart_data.set_index("date")["value"])
                        
                        # Display transaction records
                        transactions = result["transactions"]
                        if transactions:
                            st.markdown("### 📋 Transaction History")
                            txn_df = pd.DataFrame(transactions)
                            txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
                            st.dataframe(txn_df, use_container_width=True)
                    
                    else:
                        st.error(f"❌ Backtest failed: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")

def show_performance_analysis():
    """Display performance analysis page"""
    st.subheader("📊 Performance Analysis")
    st.info("Performance analysis features coming soon...")
    st.markdown("Coming soon:")
    st.markdown("- Detailed transaction history analysis")
    st.markdown("- Risk metrics calculation")
    st.markdown("- Strategy comparison analysis")
    st.markdown("- Monthly/annual performance reports")


def show_automated_trading():
    """Display automated trading page"""
    st.header("🤖 Automated Trading")

    # Check if simulation components are available
    if not SIMULATION_AVAILABLE:
        st.error("❌ Simulation trading components are not available")
        return

    # Select account
    user_id = "demo_user"
    accounts = st.session_state.simulation_manager.get_user_accounts(user_id)

    if not accounts:
        st.warning("Please create a simulation account first in Account Management")
        return

    account_id = st.selectbox(
        "Select Trading Account",
        [acc.account_id for acc in accounts],
        format_func=lambda x: next(acc.account_name for acc in accounts if acc.account_id == x),
        key="auto_trade_account"
    )

    account = next(acc for acc in accounts if acc.account_id == account_id)

    # Display account status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Available Funds", f"${account.available_balance:,.0f}")
    with col2:
        st.metric("Total Assets", f"${account.total_value:,.0f}")
    with col3:
        st.metric("Return Rate", f"{account.total_return:+.1f}%")

    st.markdown("---")

    # Portfolio selection for automated trading
    portfolios = st.session_state.portfolio_manager.list_portfolios()

    if not portfolios:
        st.warning("No portfolios available. Create a portfolio first to use automated trading.")
        return

    portfolio_options = {p.name: f"{p.name} ({len(p.holdings)} stocks)" for p in portfolios}
    selected_portfolio_name = st.selectbox(
        "Select Portfolio for Automated Trading",
        options=list(portfolio_options.keys()),
        format_func=lambda x: portfolio_options[x],
        key="auto_trade_portfolio"
    )

    selected_portfolio = st.session_state.portfolio_manager.get_portfolio(selected_portfolio_name)

    # Display portfolio information
    st.markdown("### 📁 Selected Portfolio")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Stocks", len(selected_portfolio.holdings))
    with col2:
        st.metric("Strategy", selected_portfolio.strategy_type.value.title())
    with col3:
        st.metric("Created", selected_portfolio.created_time.strftime("%Y-%m-%d"))

    # List portfolio stocks
    if selected_portfolio.holdings:
        st.markdown("**Portfolio Stocks:**")
        stocks_text = ", ".join([f"{h.symbol} ({h.weight:.1f}%)" for h in selected_portfolio.holdings])
        st.info(stocks_text)

    st.markdown("---")

    # Trading configuration
    col1, col2, col3 = st.columns(3)

    with col1:
        investment_amount = st.number_input(
            "Investment Amount ($)",
            min_value=100.0,
            max_value=float(account.available_balance),
            value=min(10000.0, float(account.available_balance)),
            step=100.0,
            key="auto_trade_amount"
        )

    with col2:
        risk_level = st.selectbox(
            "Risk Level",
            ["conservative", "moderate", "aggressive"],
            format_func=lambda x: {
                "conservative": "Conservative (Low Risk)",
                "moderate": "Moderate (Balanced)",
                "aggressive": "Aggressive (High Risk)"
            }.get(x, x),
            key="auto_trade_risk"
        )

    with col3:
        analysis_method = st.selectbox(
            "Analysis Method",
            ["comprehensive", "technical", "fundamental"],
            format_func=lambda x: {
                "comprehensive": "Comprehensive",
                "technical": "Technical Only",
                "fundamental": "Fundamental Only"
            }.get(x, x),
            key="auto_trade_analysis"
        )

    # Execute automated trading
    if st.button("🚀 Execute Automated Trading", type="primary", key="execute_auto_trade"):
        if not selected_portfolio.holdings:
            st.error("❌ Selected portfolio has no stocks to analyze")
            return

        selected_stocks = [h.symbol for h in selected_portfolio.holdings]

        with st.spinner("🤖 Analyzing stocks and generating recommendations..."):
            try:
                # Import required components
                from src.engines.recommendation_engine import RecommendationEngine
                from src.analyzers.stock_analyzer import StockAnalyzer
                from src.languages.config import LanguageConfig

                # Generate recommendations
                recommendations = []
                lang_config = LanguageConfig("en")

                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, symbol in enumerate(selected_stocks):
                    try:
                        status_text.text(f"🔍 Analyzing {symbol}...")
                        progress_bar.progress((i) / len(selected_stocks))

                        # Create analyzer
                        analyzer = StockAnalyzer(symbol)
                        analyzer.fetch_data()

                        # Map analysis method to strategy type
                        strategy_mapping = {
                            "comprehensive": "all",
                            "technical": "technical",
                            "fundamental": "quantitative"
                        }
                        strategy_type = strategy_mapping.get(analysis_method, "all")

                        # Generate recommendation
                        recommendation_engine = RecommendationEngine(analyzer, lang_config)
                        recommendation = recommendation_engine.generate_recommendation_for_symbol(
                            analyzer, symbol, strategy_type
                        )

                        recommendations.append(recommendation)

                    except Exception as e:
                        st.warning(f"⚠️ Failed to analyze {symbol}: {str(e)}")
                        continue

                progress_bar.progress(1.0)
                status_text.text("✅ Analysis completed!")

                if not recommendations:
                    st.error("❌ No valid recommendations generated")
                    return

                # Execute automated trading
                status_text.text("💰 Executing automated trades...")
                result = st.session_state.automated_trader.execute_portfolio_recommendations(
                    account.account_id,
                    recommendations,
                    available_cash=investment_amount
                )

                if result["success"]:
                    st.success("✅ Automated trading completed successfully!")

                    # Display results
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Successful Trades", result["successful_trades"])
                    with col2:
                        st.metric("Failed Trades", result["failed_trades_count"])
                    with col3:
                        st.metric("Total Invested", f"${result['total_invested']:,.0f}")
                    with col4:
                        st.metric("Recommendations", len(recommendations))

                    # Account status update
                    if result["account_summary"]:
                        acc = result["account_summary"]["account"]
                        st.markdown("### 📊 Account Status Update")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Current Balance", f"${acc.current_balance:,.2f}")
                        with col2:
                            st.metric("Total Value", f"${acc.total_value:,.2f}")
                        with col3:
                            st.metric("Total Return", f"{acc.total_return:+.1f}%")

                    # Executed trade details
                    if result["executed_trades"]:
                        st.markdown("### 💼 Executed Trades")
                        for trade in result["executed_trades"]:
                            with st.expander(f"{trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}"):
                                st.write(f"Amount: ${trade['amount']:,.2f}")
                                if 'recommendation' in trade:
                                    rec = trade['recommendation']['recommendation']
                                    st.write(f"AI Recommendation: {rec['action']} (confidence: {rec['confidence']})")

                    # Failed trades
                    if result["failed_trades"]:
                        st.markdown("### ❌ Failed Trades")
                        for trade in result["failed_trades"]:
                            st.error(f"{trade['action']} {trade['symbol']}: {trade['error']}")

                else:
                    st.error(f"❌ Automated trading failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"❌ Error during automated trading: {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()

    # Usage instructions
    with st.expander("📖 Usage Instructions"):
        st.markdown("""
        **AI-Based Automated Trading Feature:**

        1. **Smart Analysis**: AI analyzes technical indicators and market trends of selected stocks
        2. **Automated Decision**: Generates buy/sell/hold recommendations based on analysis results
        3. **Smart Execution**: Automatically allocates funds and executes recommended trades
        4. **Risk Control**: Includes trade validation and capital adequacy checks

        **Important Notes:**
        - This is a simulation trading environment, no real money loss will occur
        - AI recommendations are for reference only, not investment advice
        - Please review analysis results before deciding to execute trades
        """)


def show_backtesting():
    """Display historical backtesting page"""
    st.header("📈 Historical Backtesting")

    with st.form("backtest_form"):
        st.subheader("Backtest Settings")

        col1, col2 = st.columns(2)

        with col1:
            symbols = st.multiselect(
                "Select Stocks",
                ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
                default=["AAPL", "MSFT"]
            )

            strategy = st.selectbox(
                "Investment Strategy",
                ["buy_and_hold", "mean_reversion"],
                format_func=lambda x: {
                    "buy_and_hold": "Buy and Hold",
                    "mean_reversion": "Mean Reversion"
                }.get(x, x)
            )

        with col2:
            start_date = st.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
            end_date = st.date_input("End Date", value=pd.to_datetime("2023-12-31"))
            initial_balance = st.number_input("Initial Balance", min_value=1000, value=100000)

        submitted = st.form_submit_button("Start Backtest", type="primary")

        if submitted and symbols:
            with st.spinner("Running historical backtest..."):
                try:
                    result = st.session_state.backtest_engine.run_backtest(
                        strategy_config={"type": strategy},
                        symbols=symbols,
                        start_date=pd.to_datetime(start_date),
                        end_date=pd.to_datetime(end_date),
                        initial_balance=initial_balance
                    )

                    if result.get("success"):
                        st.success("✅ Backtest completed!")

                        # Display results
                        perf = result["performance"]

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Total Return", f"{perf['total_return']:+.1f}%")
                        with col2:
                            st.metric("Annualized Return", f"{perf['annualized_return']:+.1f}%")
                        with col3:
                            st.metric("Max Drawdown", f"{perf['max_drawdown']:.1f}%")
                        with col4:
                            st.metric("Sharpe Ratio", f"{perf['sharpe_ratio']:.2f}")

                        # Display portfolio value curve
                        portfolio_values = result["portfolio_values"]
                        if portfolio_values:
                            chart_data = pd.DataFrame(portfolio_values)
                            chart_data["date"] = pd.to_datetime(chart_data["date"])

                            st.subheader("📊 Portfolio Value Curve")
                            st.line_chart(chart_data.set_index("date")["value"])

                        # Display transaction records
                        transactions = result["transactions"]
                        if transactions:
                            st.subheader("📋 Transaction Records")
                            txn_df = pd.DataFrame(transactions)
                            txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
                            st.dataframe(txn_df, use_container_width=True)

                    else:
                        st.error(f"❌ Backtest failed: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")


# Main application
def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()
    
    # Initialize simulation components
    if SIMULATION_AVAILABLE:
        if 'simulation_manager' not in st.session_state:
            st.session_state.simulation_manager = SimulationAccountManager()
        if 'virtual_trader' not in st.session_state:
            st.session_state.virtual_trader = VirtualTrader(st.session_state.simulation_manager)
        if 'backtest_engine' not in st.session_state:
            st.session_state.backtest_engine = BacktestEngine()
        if 'automated_trader' not in st.session_state:
            st.session_state.automated_trader = AutomatedTrader(
                st.session_state.simulation_manager,
                st.session_state.virtual_trader
            )
    
    # Sidebar navigation
    st.sidebar.title("📊 Portfolio Manager")
    
    pages = {
        "🏠 Dashboard": show_dashboard,
        "💼 Portfolio Management": show_portfolio_management,
        "🔍 Portfolio Analysis": show_portfolio_analysis,
        "🆚 Portfolio Comparison": show_portfolio_comparison,
        "🎮 Simulation Trading": show_simulation if SIMULATION_AVAILABLE else show_simulation_unavailable,
        "⚙️ Settings": show_settings
    }
    
    selected_page = st.sidebar.selectbox("Navigation", options=list(pages.keys()))
    
    # Show portfolio summary in sidebar
    portfolios = st.session_state.portfolio_manager.list_portfolios()
    
    if portfolios:
        st.sidebar.subheader("📈 Quick Portfolio Stats")
        
        for portfolio in portfolios[:3]:  # Show top 3
            with st.sidebar.expander(f"{portfolio.name}"):
                st.write(f"Strategy: {portfolio.strategy_type.value.title()}")
                st.write(f"Holdings: {len(portfolio.holdings)}")
                st.write(f"Weight: {portfolio.total_weight:.1%}")
        
        if len(portfolios) > 3:
            st.sidebar.write(f"... and {len(portfolios) - 3} more portfolios")
    else:
        st.sidebar.info("No portfolios yet. Create your first portfolio!")
    
    # Run selected page
    pages[selected_page]()


if __name__ == "__main__":
    main()