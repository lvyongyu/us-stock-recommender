"""
Simulation Trading System - Historical Backtesting Engine
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .models import SimulationAccount, VirtualTransaction, TransactionType, OrderType

class BacktestEngine:
    """Historical backtesting engine"""

    def __init__(self):
        self.transaction_fee_rate = 0.001  # 0.1% transaction fee

    def run_backtest(self, strategy_config: Dict[str, Any],
                    symbols: List[str],
                    start_date: datetime,
                    end_date: datetime,
                    initial_balance: float = 100000.0) -> Dict[str, Any]:
        """
        Run historical backtest

        Args:
            strategy_config: Strategy configuration
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            initial_balance: Initial balance

        Returns:
            Backtest result dictionary
        """
        backtest_id = f"bt_{int(datetime.now().timestamp())}"

        # Get historical data
        historical_data = self._get_historical_data(symbols, start_date, end_date)

        if historical_data.empty:
            return {
                "backtest_id": backtest_id,
                "error": "Unable to get historical data",
                "success": False
            }

        # Initialize account
        account = SimulationAccount(
            account_id=f"backtest_{backtest_id}",
            user_id="backtest",
            account_name="Historical Backtest",
            initial_balance=initial_balance,
            current_balance=initial_balance,
            total_value=initial_balance,
            total_return=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Execute backtest
        portfolio_values = []
        transactions = []
        positions = {}

        current_balance = initial_balance

        for date in historical_data.index:
            # Get daily prices
            daily_prices = historical_data.loc[date]

            # Execute strategy
            trades = self._execute_strategy(strategy_config, positions, daily_prices, current_balance)

            # Execute trades
            for trade in trades:
                transaction = self._execute_trade(trade, date, account.account_id)
                transactions.append(transaction)

                # Update balance and positions
                if trade['action'] == 'BUY':      
                    current_balance -= (transaction.total_amount + transaction.fee)
                    if trade['symbol'] not in positions:
                        positions[trade['symbol']] = 0
                    positions[trade['symbol']] += trade['quantity']
                else:  # SELL
                    current_balance += (transaction.total_amount - transaction.fee)
                    positions[trade['symbol']] -= trade['quantity']

            # Calculate daily portfolio value
            portfolio_value = current_balance
            for symbol, quantity in positions.items():
                if quantity > 0 and symbol in daily_prices:
                    portfolio_value += quantity * daily_prices[symbol]

            portfolio_values.append(portfolio_value)

        # Calculate performance metrics
        performance = self._calculate_performance(portfolio_values, [self._transaction_to_dict(txn) for txn in transactions])

        return {
            "backtest_id": backtest_id,
            "success": True,
            "strategy": strategy_config,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "initial_balance": initial_balance,
            "final_balance": portfolio_values[-1] if portfolio_values else initial_balance,
            "performance": performance,
            "portfolio_values": portfolio_values,
            "transactions": [self._transaction_to_dict(txn) for txn in transactions],
            "total_trades": len(transactions)
        }

    def _get_historical_data(self, symbols: List[str], start_date: datetime,
                           end_date: datetime) -> pd.DataFrame:
        """Get historical data from real stock market"""
        try:
            import yfinance as yf
        except ImportError:
            print("Warning: yfinance not installed, falling back to simulated data")
            return self._get_simulated_data(symbols, start_date, end_date)

        print(f"📊 Fetching real stock data for {len(symbols)} symbols from {start_date.date()} to {end_date.date()}")

        # Download data for all symbols at once
        try:
            data = yf.download(
                symbols,
                start=start_date,
                end=end_date,
                progress=False,
                group_by='ticker'
            )

            # Handle single symbol case
            if len(symbols) == 1:
                symbol = symbols[0]
                if 'Close' in data.columns:
                    # Single symbol returns DataFrame with Close, Open, etc. columns
                    df = pd.DataFrame({
                        symbol: data['Close']
                    })
                else:
                    # Fallback to simulated data if no data
                    print(f"⚠️  No data available for {symbol}, using simulated data")
                    return self._get_simulated_data(symbols, start_date, end_date)
            else:
                # Multiple symbols case
                df = pd.DataFrame()
                for symbol in symbols:
                    if symbol in data.columns.levels[0]:
                        df[symbol] = data[symbol]['Close']
                    else:
                        print(f"⚠️  No data available for {symbol}, using simulated price")
                        # Add simulated data for missing symbols
                        sim_data = self._get_simulated_data([symbol], start_date, end_date)
                        df[symbol] = sim_data[symbol]

            # Remove any NaN values and ensure we have data
            df = df.dropna()

            if df.empty:
                print("⚠️  No valid data found, falling back to simulated data")
                return self._get_simulated_data(symbols, start_date, end_date)

            print(f"✅ Successfully loaded {len(df)} days of real stock data")
            return df

        except Exception as e:
            print(f"⚠️  Error fetching real data: {e}, falling back to simulated data")
            return self._get_simulated_data(symbols, start_date, end_date)

    def _get_simulated_data(self, symbols: List[str], start_date: datetime,
                           end_date: datetime) -> pd.DataFrame:
        """Get simulated data (fallback method)"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        np.random.seed(42)  # Fixed random seed for reproducibility

        data = {}
        for symbol in symbols:
            # Generate simulated price data (random walk)
            base_price = 100.0
            prices = [base_price]
            for _ in range(len(date_range) - 1):
                change = np.random.normal(0, 0.02)  # 2% volatility
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 1.0))  # Price not below $1

            data[symbol] = prices

        df = pd.DataFrame(data, index=date_range)
        return df

    def _execute_strategy(self, strategy_config: Dict[str, Any],
                         positions: Dict[str, int], daily_prices: pd.Series,
                         current_balance: float) -> List[Dict[str, Any]]:
        """Execute strategy"""
        trades = []
        strategy_type = strategy_config.get('type', 'buy_and_hold')

        if strategy_type == 'buy_and_hold':
            # Buy and hold strategy: buy if no positions and have cash
            if not positions and current_balance > 1000:
                # Buy the cheapest stock
                cheapest_symbol = daily_prices.idxmin()
                price = daily_prices[cheapest_symbol]
                quantity = int((current_balance * 0.9) / price)  # Use 90% of cash

                if quantity > 0:
                    trades.append({
                        'action': 'BUY',
                        'symbol': cheapest_symbol,
                        'quantity': quantity,
                        'price': price
                    })

        elif strategy_type == 'mean_reversion':
            # Mean reversion strategy: trade when price deviates from mean
            for symbol, price in daily_prices.items():
                # Simple implementation: buy below $90, sell above $110
                if price < 90 and current_balance > price * 10:
                    quantity = min(10, int(current_balance / price))
                    if quantity > 0:
                        trades.append({
                            'action': 'BUY',
                            'symbol': symbol,
                            'quantity': quantity,
                            'price': price
                        })
                elif price > 110 and positions.get(symbol, 0) > 0:
                    quantity = min(positions[symbol], 5)
                    trades.append({
                        'action': 'SELL',
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': price
                    })

        return trades

    def _execute_trade(self, trade: Dict[str, Any], date: datetime,
                      account_id: str) -> VirtualTransaction:
        """Execute trade"""
        return VirtualTransaction(
            transaction_id=f"bt_txn_{int(date.timestamp())}_{trade['symbol']}",
            account_id=account_id,
            symbol=trade['symbol'],
            transaction_type=TransactionType.BUY if trade['action'] == 'BUY' else TransactionType.SELL,
            order_type=OrderType.MARKET,
            quantity=trade['quantity'],
            price=trade['price'],
            total_amount=trade['quantity'] * trade['price'],
            fee=trade['quantity'] * trade['price'] * self.transaction_fee_rate,
            timestamp=date
        )

    def _calculate_performance(self, portfolio_values: List[float],
                              trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if len(portfolio_values) < 2:
            return {
                'total_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'total_trades': 0
            }

        # Calculate returns
        returns = pd.Series(portfolio_values).pct_change().dropna()

        # Total return
        total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]

        # Sharpe ratio (annualized, assuming daily returns)
        if returns.std() > 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)  # 252 trading days
        else:
            sharpe_ratio = 0.0

        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Win rate
        profitable_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
        total_trades = len(trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0.0

        # Annualized return (assuming daily data)
        total_days = len(portfolio_values) - 1
        if total_days > 0:
            annualized_return = (1 + total_return) ** (252 / total_days) - 1  # 252 trading days per year
        else:
            annualized_return = 0.0

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_days': total_days,
            'total_trades': total_trades
        }

    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(values) < 2:
            return 0.0

        peak = values[0]
        max_drawdown = 0.0

        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown

    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0

        avg_return = sum(returns) / len(returns)
        std_return = pd.Series(returns).std()

        if std_return == 0:
            return 0.0

        # Annualized Sharpe ratio
        annualized_avg_return = avg_return * 252  # Assuming 252 trading days
        annualized_std = std_return * (252 ** 0.5)
        annualized_risk_free = risk_free_rate

        return (annualized_avg_return - annualized_risk_free) / annualized_std

    def _transaction_to_dict(self, transaction: VirtualTransaction) -> Dict[str, Any]:
        """Convert transaction record to dictionary"""
        return {
            "transaction_id": transaction.transaction_id,
            "symbol": transaction.symbol,
            "type": transaction.transaction_type.value,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "total_amount": transaction.total_amount,
            "fee": transaction.fee,
            "timestamp": transaction.timestamp.isoformat()
        }