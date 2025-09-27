"""
Simulation Trading System - Automated Trading Engine

Automatically executes trades based on portfolio analysis and recommendations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from .account_manager import SimulationAccountManager
from .trader import VirtualTrader
from .models import TransactionType, OrderType


class AutomatedTrader:
    """Automated trading engine based on portfolio recommendations"""

    def __init__(self, account_manager: SimulationAccountManager,
                 virtual_trader: VirtualTrader):
        self.account_manager = account_manager
        self.virtual_trader = virtual_trader

    def execute_portfolio_recommendations(self, account_id: str,
                                        recommendations: List[Dict[str, Any]],
                                        available_cash: float = None) -> Dict[str, Any]:
        """
        Execute trading recommendations for a portfolio

        Args:
            account_id: Simulation account ID
            recommendations: List of recommendation dictionaries
            available_cash: Available cash for buying (if None, use account balance)

        Returns:
            Execution results dictionary
        """
        account = self.account_manager.get_account(account_id)
        if not account:
            return {"success": False, "error": "Account not found"}

        if available_cash is None:
            available_cash = account.available_balance

        executed_trades = []
        failed_trades = []
        total_invested = 0.0

        print(f"🤖 Starting automated trading for account {account_id}")
        print(f"💰 Available cash: ${available_cash:,.2f}")

        # Get current positions
        current_positions = self.account_manager.calculate_positions(account_id)
        current_symbols = set(current_positions.keys())

        # Categorize recommendations
        buy_recommendations = []
        sell_recommendations = []
        hold_recommendations = []

        for rec in recommendations:
            action = rec.get('recommendation', {}).get('action', '').lower()
            if 'buy' in action or '买入' in action:
                buy_recommendations.append(rec)
            elif 'sell' in action or '卖出' in action:
                sell_recommendations.append(rec)
            else:
                hold_recommendations.append(rec)

        print(f"📊 Recommendations: {len(buy_recommendations)} BUY, {len(sell_recommendations)} SELL, {len(hold_recommendations)} HOLD")

        # Execute SELL orders first (free up cash)
        for rec in sell_recommendations:
            symbol = rec.get('symbol')
            if symbol in current_positions:
                position = current_positions[symbol]
                quantity = position.quantity

                try:
                    transaction = self.virtual_trader.execute_sell_order(
                        account_id, symbol, quantity, OrderType.MARKET
                    )
                    executed_trades.append({
                        "symbol": symbol,
                        "action": "SELL",
                        "quantity": quantity,
                        "price": transaction.price,
                        "amount": transaction.total_amount,
                        "recommendation": rec
                    })
                    available_cash += transaction.total_amount - transaction.fee
                    print(f"✅ SOLD {quantity} shares of {symbol} @ ${transaction.price:.2f}")
                except Exception as e:
                    failed_trades.append({
                        "symbol": symbol,
                        "action": "SELL",
                        "error": str(e),
                        "recommendation": rec
                    })
                    print(f"❌ Failed to sell {symbol}: {e}")

        # Execute BUY orders
        if buy_recommendations:
            # Calculate cash allocation per buy recommendation
            cash_per_buy = available_cash / len(buy_recommendations)

            for rec in buy_recommendations:
                symbol = rec.get('symbol')
                current_price = rec.get('current_price', 0)

                if current_price <= 0:
                    # Try to get current price
                    try:
                        current_price = self.virtual_trader._get_current_price(symbol)
                    except:
                        failed_trades.append({
                            "symbol": symbol,
                            "action": "BUY",
                            "error": "Could not get current price",
                            "recommendation": rec
                        })
                        continue

                # Calculate quantity to buy (use up to 90% of allocated cash)
                max_quantity = int((cash_per_buy * 0.9) / current_price)

                if max_quantity > 0:
                    try:
                        transaction = self.virtual_trader.execute_buy_order(
                            account_id, symbol, max_quantity, OrderType.MARKET
                        )
                        executed_trades.append({
                            "symbol": symbol,
                            "action": "BUY",
                            "quantity": max_quantity,
                            "price": transaction.price,
                            "amount": transaction.total_amount,
                            "recommendation": rec
                        })
                        total_invested += transaction.total_amount + transaction.fee
                        print(f"✅ BOUGHT {max_quantity} shares of {symbol} @ ${transaction.price:.2f}")
                    except Exception as e:
                        failed_trades.append({
                            "symbol": symbol,
                            "action": "BUY",
                            "error": str(e),
                            "recommendation": rec
                        })
                        print(f"❌ Failed to buy {symbol}: {e}")
                else:
                    failed_trades.append({
                        "symbol": symbol,
                        "action": "BUY",
                        "error": "Insufficient cash for minimum purchase",
                        "recommendation": rec
                    })

        # Update account summary
        account_summary = self.account_manager.get_account_summary(account_id)

        result = {
            "success": True,
            "account_id": account_id,
            "executed_trades": executed_trades,
            "failed_trades": failed_trades,
            "total_trades": len(executed_trades) + len(failed_trades),
            "successful_trades": len(executed_trades),
            "failed_trades_count": len(failed_trades),
            "total_invested": total_invested,
            "account_summary": account_summary,
            "execution_time": datetime.now().isoformat()
        }

        print(f"🎯 Execution completed: {len(executed_trades)} successful, {len(failed_trades)} failed")
        return result

    def get_portfolio_recommendations(self, portfolio_holdings: List[Dict[str, Any]],
                                    recommendation_engine) -> List[Dict[str, Any]]:
        """
        Get recommendations for all holdings in a portfolio

        Args:
            portfolio_holdings: List of portfolio holdings
            recommendation_engine: Instance of RecommendationEngine

        Returns:
            List of recommendations for each holding
        """
        recommendations = []

        for holding in portfolio_holdings:
            symbol = holding.get('symbol')
            if not symbol:
                continue

            try:
                # Create analyzer for this symbol
                from ..analyzers.stock_analyzer import StockAnalyzer
                analyzer = StockAnalyzer(symbol)

                # Generate recommendation
                recommendation = recommendation_engine.generate_recommendation_for_symbol(
                    analyzer, symbol
                )

                recommendations.append(recommendation)

            except Exception as e:
                print(f"⚠️  Could not get recommendation for {symbol}: {e}")
                continue

        return recommendations

    def rebalance_portfolio(self, account_id: str, target_allocations: Dict[str, float],
                          available_cash: float = None) -> Dict[str, Any]:
        """
        Rebalance portfolio to target allocations

        Args:
            account_id: Simulation account ID
            target_allocations: Target allocation percentages for each symbol
            available_cash: Available cash for rebalancing

        Returns:
            Rebalancing execution results
        """
        account = self.account_manager.get_account(account_id)
        if not account:
            return {"success": False, "error": "Account not found"}

        if available_cash is None:
            available_cash = account.available_balance

        # Get current positions and total value
        positions = self.account_manager.calculate_positions(account_id)
        total_value = account.current_balance

        for position in positions.values():
            total_value += position.market_value

        trades_to_execute = []

        # Calculate target values
        for symbol, target_pct in target_allocations.items():
            target_value = total_value * target_pct
            current_value = 0.0

            if symbol in positions:
                current_value = positions[symbol].market_value

            if current_value < target_value * 0.95:  # Need to buy
                buy_amount = target_value - current_value
                if buy_amount > 10:  # Minimum trade amount
                    current_price = self.virtual_trader._get_current_price(symbol)
                    quantity = int(buy_amount / current_price)
                    if quantity > 0:
                        trades_to_execute.append({
                            "action": "BUY",
                            "symbol": symbol,
                            "quantity": quantity
                        })

            elif current_value > target_value * 1.05:  # Need to sell
                sell_amount = current_value - target_value
                if sell_amount > 10:  # Minimum trade amount
                    current_price = self.virtual_trader._get_current_price(symbol)
                    quantity = int(sell_amount / current_price)
                    if quantity > 0 and symbol in positions:
                        available_qty = positions[symbol].quantity
                        quantity = min(quantity, available_qty)
                        if quantity > 0:
                            trades_to_execute.append({
                                "action": "SELL",
                                "symbol": symbol,
                                "quantity": quantity
                            })

        # Execute trades
        executed_trades = []
        failed_trades = []

        for trade in trades_to_execute:
            try:
                if trade["action"] == "BUY":
                    transaction = self.virtual_trader.execute_buy_order(
                        account_id, trade["symbol"], trade["quantity"], OrderType.MARKET
                    )
                else:
                    transaction = self.virtual_trader.execute_sell_order(
                        account_id, trade["symbol"], trade["quantity"], OrderType.MARKET
                    )

                executed_trades.append({
                    "symbol": trade["symbol"],
                    "action": trade["action"],
                    "quantity": trade["quantity"],
                    "price": transaction.price,
                    "amount": transaction.total_amount
                })

                print(f"✅ {trade['action']} {trade['quantity']} shares of {trade['symbol']} @ ${transaction.price:.2f}")

            except Exception as e:
                failed_trades.append({
                    "symbol": trade["symbol"],
                    "action": trade["action"],
                    "error": str(e)
                })
                print(f"❌ Failed to {trade['action']} {trade['symbol']}: {e}")

        return {
            "success": True,
            "executed_trades": executed_trades,
            "failed_trades": failed_trades,
            "account_summary": self.account_manager.get_account_summary(account_id)
        }