#!/usr/bin/env python3
"""
Simulation Trading System Demo Script

Shows how to use various features of the simulation trading system
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
from src.simulation.backtest_engine import BacktestEngine
from src.simulation.models import TransactionType, OrderType

def demo_simulation_system():
    """Demonstrate simulation trading system features"""
    print("🎮 Simulation Trading System Demo")
    print("=" * 50)

    # Initialize components
    account_manager = SimulationAccountManager()
    virtual_trader = VirtualTrader(account_manager)
    backtest_engine = BacktestEngine()

    # 1. Create simulation account
    print("\\n1. Create Simulation Account")
    user_id = "demo_user"
    account = account_manager.create_account(
        user_id=user_id,
        account_name="Demo Account",
        initial_balance=100000.0
    )
    print(f"✅ Account created successfully: {account.account_name}")
    print(f"   Account ID: {account.account_id}")
    print(f"   Initial balance: ${account.initial_balance:,.0f}")

    # 2. Execute virtual trading
    print("\\n2. Execute Virtual Trading")

    # Buy AAPL
    try:
        buy_transaction = virtual_trader.execute_buy_order(
            account.account_id, "AAPL", 50, OrderType.MARKET
        )
        print(f"✅ Buy AAPL: {buy_transaction.quantity} shares @ ${buy_transaction.price:.2f}")
        print(f"   Total amount: ${buy_transaction.total_amount:.2f}, Fee: ${buy_transaction.fee:.2f}")
    except Exception as e:
        print(f"❌ Buy failed: {e}")

    # Buy MSFT
    try:
        buy_transaction2 = virtual_trader.execute_buy_order(
            account.account_id, "MSFT", 30, OrderType.MARKET
        )
        print(f"✅ Buy MSFT: {buy_transaction2.quantity} shares @ ${buy_transaction2.price:.2f}")
    except Exception as e:
        print(f"❌ Buy failed: {e}")

    # 3. View account status
    print("\\n3. View Account Status")
    account_summary = account_manager.get_account_summary(account.account_id)

    if account_summary:
        acc = account_summary['account']
        positions = account_summary['positions']

        print(f"💰 Account balance: ${acc.current_balance:,.0f}")
        print(f"📊 Total assets: ${acc.total_value:,.0f}")
        print(f"📈 Total return: {acc.total_return:+.1f}%")

        print(f"\\n📋 Position details:")
        for symbol, position in positions.items():
            print(f"   {symbol}: {position.quantity} shares @ ${position.average_cost:.2f} "
                  f"(Current: ${position.current_price:.2f}, P&L: ${position.unrealized_pnl:+.2f})")

    # 4. View transaction history
    print("\\n4. View Transaction History")
    transactions = account_manager.get_transaction_history(account.account_id, limit=10)

    print("Recent transactions:")
    for txn in transactions[-5:]:  # Show last 5 transactions
        print(f"   {txn.timestamp.strftime('%Y-%m-%d %H:%M')} "
              f"{txn.transaction_type.value} {txn.symbol} {txn.quantity} shares "
              f"@ ${txn.price:.2f}")

    # 5. Execute historical backtest
    print("\\n5. Execute Historical Backtest")

    # Backtest configuration
    backtest_config = {
        "type": "buy_and_hold"  # Buy and hold strategy
    }

    symbols = ["AAPL", "MSFT", "GOOGL"]
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()

    print(f"🔍 Backtest strategy: {backtest_config['type']}")
    print(f"📅 Time range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"📊 Stock list: {', '.join(symbols)}")

    try:
        backtest_result = backtest_engine.run_backtest(
            strategy_config=backtest_config,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_balance=100000.0
        )

        if backtest_result.get("success"):
            perf = backtest_result["performance"]
            print("\\n📈 Backtest results:")
            print(f"   Total return: {perf['total_return']:+.1f}%")
            print(f"   Annualized return: {perf['annualized_return']:+.1f}%")
            print(f"   Max drawdown: {perf['max_drawdown']:.1f}%")
            print(f"   Sharpe ratio: {perf['sharpe_ratio']:.2f}")
            print(f"   Win rate: {perf['win_rate']:.1%}")
            print(f"   Total trading days: {perf['total_days']}")
            print(f"   Total trades: {backtest_result['total_trades']}")

            final_balance = backtest_result["final_balance"]
            print(f"   Final balance: ${final_balance:,.0f}")
        else:
            print(f"❌ Backtest failed: {backtest_result.get('error')}")

    except Exception as e:
        print(f"❌ Backtest exception: {e}")

    # 6. Clean up demo data
    print("\\n6. Clean Up Demo Data")
    # Note: Don't easily delete data in real usage, this is just for demo

    print("\\n🎉 Simulation Trading System Demo Completed!")
    print("\\nMain features:")
    print("✅ Simulation account management")
    print("✅ Virtual trading execution")
    print("✅ Position and P&L calculation")
    print("✅ Transaction history recording")
    print("✅ Historical backtest analysis")
    print("✅ Performance metrics calculation")

if __name__ == "__main__":
    demo_simulation_system()