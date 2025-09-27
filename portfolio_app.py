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
except ImportError as e:
    st.error(f"Failed to import portfolio components: {e}")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="US Stock Recommender - Portfolio Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/lvyongyu/us-stock-recommender',
        'Report a bug': 'https://github.com/lvyongyu/us-stock-recommender/issues',
        'About': "# US Stock Recommender\nA comprehensive stock analysis and portfolio management system"
    }
)

# Custom CSS for better styling and Safari compatibility
st.markdown("""
<style>
    /* Safari compatibility improvements */
    * {
        -webkit-box-sizing: border-box;
        -moz-box-sizing: border-box;
        box-sizing: border-box;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        -webkit-font-smoothing: antialiased;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        -webkit-border-radius: 0.5rem;
        -moz-border-radius: 0.5rem;
    }
    
    .success-alert {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
        -webkit-border-radius: 0.25rem;
        -moz-border-radius: 0.25rem;
    }
    
    .warning-alert {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #ffeaa7;
        -webkit-border-radius: 0.25rem;
        -moz-border-radius: 0.25rem;
    }
    
    .error-alert {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
        -webkit-border-radius: 0.25rem;
        -moz-border-radius: 0.25rem;
    }
    
    /* Safari specific fixes */
    @media screen and (-webkit-min-device-pixel-ratio:0) {
        select {
            -webkit-appearance: none;
            appearance: none;
        }
        
        input[type="text"], input[type="number"] {
            -webkit-appearance: none;
            -webkit-border-radius: 0;
        }
        
        button {
            -webkit-appearance: none;
            -webkit-border-radius: 0;
        }
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
    
    # Safari compatibility check
    if 'browser_checked' not in st.session_state:
        st.session_state.browser_checked = True
        # Add browser compatibility notice
        st.markdown("""
        <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #2196f3;">
            <h4 style="color: #1565c0; margin: 0 0 0.5rem 0;">🌐 浏览器兼容性提示</h4>
            <p style="margin: 0; color: #1565c0;">
                如果在 Safari 中遇到访问问题，建议：<br>
                • 清除 Safari 缓存和网站数据<br>
                • 禁用内容阻止器和广告拦截器<br>
                • 或使用 Chrome/Firefox 获得最佳体验
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    if 'selected_portfolio' not in st.session_state:
        st.session_state.selected_portfolio = None
    
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}


# Utility functions
def get_strategy_color(strategy_type: StrategyType) -> str:
    """Get color for strategy type."""
    colors = {
        StrategyType.CONSERVATIVE: "#28a745",
        StrategyType.BALANCED: "#ffc107", 
        StrategyType.AGGRESSIVE: "#dc3545"
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
            portfolio_data.append({
                'Name': portfolio.name,
                'Strategy': portfolio.strategy_type.value.title(),
                'Holdings': len(portfolio.holdings),
                'Total Weight': f"{portfolio.total_weight:.1%}",
                'Expected Return': f"{analysis['portfolio_metrics']['expected_return']:.1%}",
                'Risk Level': analysis['risk_assessment']['risk_level'],
                'Recommendation': analysis['overall_recommendation']['recommendation']
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
                    options=[StrategyType.CONSERVATIVE, StrategyType.BALANCED, StrategyType.AGGRESSIVE],
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
                            options=[StrategyType.CONSERVATIVE, StrategyType.BALANCED, StrategyType.AGGRESSIVE],
                            index=[StrategyType.CONSERVATIVE, StrategyType.BALANCED, StrategyType.AGGRESSIVE].index(portfolio.strategy_type),
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
                with st.form("add_stock"):
                    st.write("Add New Stock")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        stock_symbol = st.text_input("Symbol", placeholder="e.g., AAPL").upper()
                    
                    with col2:
                        weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
                    
                    with col3:
                        target_weight = st.number_input("Target Weight (%)", min_value=0.0, max_value=100.0, value=weight, step=0.1)
                    
                    with col4:
                        st.write("")  # Spacing
                        st.write("")  # Spacing
                        add_stock = st.form_submit_button("Add Stock")
                    
                    notes = st.text_input("Notes (optional)", placeholder="Investment thesis or notes...")
                    
                    if add_stock:
                        if stock_symbol:
                            try:
                                manager.add_stock(
                                    selected_portfolio_name,
                                    stock_symbol,
                                    weight / 100,
                                    target_weight=target_weight / 100 if target_weight != weight else None,
                                    notes=notes if notes else None
                                )
                                st.success(f"✅ Added {stock_symbol} to portfolio!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error adding stock: {e}")
                        else:
                            st.warning("⚠️ Please provide a stock symbol.")
                
                # Current holdings
                if portfolio.holdings:
                    st.write("**Current Holdings**")
                    
                    holdings_data = []
                    for holding in portfolio.holdings:
                        deviation = holding.get_weight_deviation()
                        holdings_data.append({
                            'Symbol': holding.symbol,
                            'Weight': f"{holding.weight:.1%}",
                            'Target Weight': f"{holding.target_weight:.1%}" if holding.target_weight else "N/A",
                            'Deviation': f"{deviation:+.1%}" if deviation else "N/A",
                            'Notes': holding.notes or ""
                        })
                    
                    df_holdings = pd.DataFrame(holdings_data)
                    st.dataframe(df_holdings, use_container_width=True)
                    
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
        
        # Individual stock analysis
        st.subheader("📈 Individual Stock Analysis")
        
        individual = analysis['individual_analysis']
        
        stock_data = []
        for symbol, stock_analysis in individual.items():
            stock_data.append({
                'Symbol': symbol,
                'Weight': f"{stock_analysis['weight']:.1%}",
                'Recommendation': stock_analysis['recommendation'],
                'Confidence': f"{stock_analysis['confidence']:.1%}",
                'Risk Score': f"{stock_analysis['risk_score']:.2f}",
                'Expected Return': f"{stock_analysis['expected_return']:.1%}"
            })
        
        if stock_data:
            df_stocks = pd.DataFrame(stock_data)
            st.dataframe(df_stocks, use_container_width=True)
        
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
                value1_str = f"{value1:{format_str}}"
                value2_str = f"{value2:{format_str}}"
            else:
                value1_str = str(value1)
                value2_str = str(value2)
            
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
        format_func=lambda x: 'English' if x == 'en' else '中文'
    )
    
    if new_language != current_language:
        st.session_state.portfolio_analyzer = PortfolioAnalyzer(language=new_language)
        st.success(f"✅ Language changed to {'English' if new_language == 'en' else '中文'}")
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


# Main application
def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("📊 Portfolio Manager")
    
    pages = {
        "🏠 Dashboard": show_dashboard,
        "💼 Portfolio Management": show_portfolio_management,
        "🔍 Portfolio Analysis": show_portfolio_analysis,
        "🆚 Portfolio Comparison": show_portfolio_comparison,
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