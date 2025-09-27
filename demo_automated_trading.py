#!/usr/bin/env python3
"""
Automated Trading Demo - Execute trades based on portfolio recommendations

Shows how to automatically execute BUY/SELL/HOLD operations based on
portfolio analysis and stock recommendations
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.simulation.account_manager import SimulationAccountManager
from src.simulation.trader import VirtualTrader
from src.simulation.automated_trader import AutomatedTrader
from src.engines.recommendation_engine import RecommendationEngine
from src.analyzers.stock_analyzer import StockAnalyzer
from src.languages.config import LanguageConfig

def demo_automated_trading():
    """Demonstrate automated trading based on recommendations"""
    print("🤖 Automated Trading Demo")
    print("=" * 50)

    # Initialize components
    account_manager = SimulationAccountManager()
    virtual_trader = VirtualTrader(account_manager)
    automated_trader = AutomatedTrader(account_manager, virtual_trader)

    # Create demo account
    user_id = "auto_trader_demo"
    account = account_manager.create_account(
        user_id=user_id,
        account_name="Automated Trading Demo",
        initial_balance=50000.0
    )
    print(f"✅ Demo account created: {account.account_name}")
    print(f"   Account ID: {account.account_id}")
    print(f"   Initial balance: ${account.initial_balance:,.0f}")

    # Define portfolio holdings to analyze
    portfolio_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

    print(f"\\n📊 Analyzing portfolio: {', '.join(portfolio_symbols)}")

    # Get recommendations for each stock
    recommendations = []
    lang_config = LanguageConfig("en")

    for symbol in portfolio_symbols:
        try:
            print(f"\\n🔍 Analyzing {symbol}...")

            # Create analyzer for the stock
            analyzer = StockAnalyzer(symbol)

            # Fetch data first
            print(f"   📡 Fetching data for {symbol}...")
            analyzer.fetch_data()

            # Create recommendation engine
            recommendation_engine = RecommendationEngine(analyzer, lang_config)

            # Generate recommendation
            recommendation = recommendation_engine.generate_recommendation_for_symbol(
                analyzer, symbol, 'combined'
            )

            recommendations.append(recommendation)

            # Display recommendation
            rec = recommendation['recommendation']
            print(f"   ✅ Action: {rec['action']}")
            print(f"   Confidence: {rec['confidence']}")
            print(f"   Current Price: ${recommendation['current_price']:.2f}")

        except Exception as e:
            print(f"   ❌ Error analyzing {symbol}: {e}")
            continue

    print(f"\\n🎯 Executing automated trades based on {len(recommendations)} recommendations...")

    # Execute automated trading
    result = automated_trader.execute_portfolio_recommendations(
        account.account_id,
        recommendations,
        available_cash=40000.0  # Use $40k for trading
    )

    if result["success"]:
        print("\\n✅ Automated trading completed!")
        print(f"   Successful trades: {result['successful_trades']}")
        print(f"   Failed trades: {result['failed_trades_count']}")
        print(f"   Total invested: ${result['total_invested']:,.2f}")

        # Show final account status
        account_summary = result["account_summary"]
        if account_summary:
            acc = account_summary['account']
            positions = account_summary['positions']

            print("\\n📊 Final Account Status:")
            print(f"   Cash balance: ${acc.current_balance:,.2f}")
            print(f"   Total value: ${acc.total_value:,.2f}")
            print(f"   Total return: {acc.total_return:+.1f}%")

            if positions:
                print("\\n📋 Positions:")
                for symbol, position in positions.items():
                    print(f"   {symbol}: {position.quantity} shares @ ${position.average_cost:.2f} "
                          f"(Current: ${position.current_price:.2f}, P&L: ${position.unrealized_pnl:+.2f})")

        # Show executed trades
        if result["executed_trades"]:
            print("\\n💼 Executed Trades:")
            for trade in result["executed_trades"]:
                print(f"   {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")

        if result["failed_trades"]:
            print("\\n❌ Failed Trades:")
            for trade in result["failed_trades"]:
                print(f"   {trade['action']} {trade['symbol']}: {trade['error']}")

    else:
        print(f"❌ Automated trading failed: {result.get('error')}")

    print("\\n🎉 Automated Trading Demo Completed!")
    print("\\nKey features:")
    print("✅ Portfolio analysis integration")
    print("✅ Automated BUY/SELL execution")
    print("✅ Recommendation-based trading")
    print("✅ Real-time price integration")
    print("✅ Risk management and validation")

if __name__ == "__main__":
    demo_automated_trading()