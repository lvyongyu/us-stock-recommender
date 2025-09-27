"""
Simulation Trading System Core Classes Design

Core Entity Classes:
- SimulationAccount: Simulation account
- VirtualPosition: Virtual position
- VirtualTransaction: Virtual transaction record
- BacktestResult: Backtest result

Core Business Classes:
- SimulationManager: Simulation account manager
- VirtualTrader: Virtual trading engine
- BacktestEngine: Historical backtest engine
- PerformanceCalculator: Performance calculator
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pandas as pd

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class OrderType(Enum):
    MARKET = "MARKET"  # Market order
    LIMIT = "LIMIT"    # Limit order

@dataclass
class VirtualTransaction:
    """Virtual transaction record"""
    transaction_id: str
    account_id: str
    symbol: str
    transaction_type: TransactionType
    order_type: OrderType
    quantity: int
    price: float
    total_amount: float
    fee: float
    timestamp: datetime
    status: str = "COMPLETED"

    @property
    def net_amount(self) -> float:
        """Net transaction amount (after fees)"""
        if self.transaction_type == TransactionType.BUY:
            return -(self.total_amount + self.fee)
        else:
            return self.total_amount - self.fee

@dataclass
class VirtualPosition:
    """Virtual position"""
    account_id: str
    symbol: str
    quantity: int
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float

    @classmethod
    def from_transactions(cls, account_id: str, symbol: str,
                         transactions: List[VirtualTransaction]) -> 'VirtualPosition':
        """Calculate position from transaction records"""
        buy_transactions = [t for t in transactions
                          if t.symbol == symbol and t.transaction_type == TransactionType.BUY]

        if not buy_transactions:
            return None

        total_cost = sum(t.total_amount for t in buy_transactions)
        total_quantity = sum(t.quantity for t in buy_transactions)

        if total_quantity == 0:
            return None

        average_cost = total_cost / total_quantity

        # Need to get current price here
        current_price = 100.0  # Temporary value, need to get from StockInfoManager

        market_value = total_quantity * current_price
        unrealized_pnl = market_value - total_cost
        unrealized_pnl_pct = (unrealized_pnl / total_cost) * 100 if total_cost > 0 else 0

        return cls(
            account_id=account_id,
            symbol=symbol,
            quantity=total_quantity,
            average_cost=average_cost,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct
        )

@dataclass
class SimulationAccount:
    """Simulation account"""
    account_id: str
    user_id: str
    account_name: str
    initial_balance: float
    current_balance: float
    total_value: float  # Total assets = cash + position market value
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    @property
    def total_return(self) -> float:
        """Total return percentage"""
        return ((self.total_value - self.initial_balance) / self.initial_balance) * 100

    @property
    def available_balance(self) -> float:
        """Available funds (considering position margin requirements)"""
        # Simple implementation, may need to consider margin requirements in practice
        return self.current_balance

class SimulationManager:
    """Simulation account manager"""

    def __init__(self):
        self.accounts: Dict[str, SimulationAccount] = {}
        self.transactions: Dict[str, List[VirtualTransaction]] = {}
        self.positions: Dict[str, Dict[str, VirtualPosition]] = {}

    def create_account(self, user_id: str, account_name: str,
                      initial_balance: float = 100000.0) -> SimulationAccount:
        """Create simulation account"""
        account_id = f"sim_{user_id}_{int(datetime.now().timestamp())}"

        account = SimulationAccount(
            account_id=account_id,
            user_id=user_id,
            account_name=account_name,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            total_value=initial_balance,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.accounts[account_id] = account
        self.transactions[account_id] = []
        self.positions[account_id] = {}

        return account

    def get_account(self, account_id: str) -> Optional[SimulationAccount]:
        """Get account information"""
        return self.accounts.get(account_id)

    def update_account_value(self, account_id: str):
        """Update account total value"""
        if account_id not in self.accounts:
            return

        account = self.accounts[account_id]
        positions_value = sum(pos.market_value for pos in self.positions[account_id].values())
        account.total_value = account.current_balance + positions_value
        account.updated_at = datetime.now()

    def get_positions(self, account_id: str) -> Dict[str, VirtualPosition]:
        """Get account positions"""
        return self.positions.get(account_id, {})

    def get_transaction_history(self, account_id: str,
                              limit: int = 50) -> List[VirtualTransaction]:
        """Get transaction history"""
        transactions = self.transactions.get(account_id, [])
        return sorted(transactions, key=lambda x: x.timestamp, reverse=True)[:limit]

class VirtualTrader:
    """Virtual trading engine"""

    def __init__(self, simulation_manager: SimulationManager):
        self.simulation_manager = simulation_manager
        self.transaction_fee_rate = 0.001  # 0.1% transaction fee

    def execute_buy_order(self, account_id: str, symbol: str,
                         quantity: int, order_type: OrderType = OrderType.MARKET) -> VirtualTransaction:
        """Execute buy order"""
        account = self.simulation_manager.get_account(account_id)
        if not account:
            raise ValueError("Account not found")

        # Get current price (need to integrate StockInfoManager)
        current_price = self._get_current_price(symbol)
        total_amount = quantity * current_price
        fee = total_amount * self.transaction_fee_rate

        # Check if funds are sufficient
        if account.available_balance < (total_amount + fee):
            raise ValueError("Insufficient funds")

        # Create transaction record
        transaction = VirtualTransaction(
            transaction_id=f"txn_{account_id}_{int(datetime.now().timestamp())}",
            account_id=account_id,
            symbol=symbol,
            transaction_type=TransactionType.BUY,
            order_type=order_type,
            quantity=quantity,
            price=current_price,
            total_amount=total_amount,
            fee=fee,
            timestamp=datetime.now()
        )

        # Update account balance
        account.current_balance -= (total_amount + fee)
        self.simulation_manager.transactions[account_id].append(transaction)

        # Update positions
        self._update_positions(account_id)

        return transaction

    def execute_sell_order(self, account_id: str, symbol: str,
                          quantity: int, order_type: OrderType = OrderType.MARKET) -> VirtualTransaction:
        """Execute sell order"""
        account = self.simulation_manager.get_account(account_id)
        if not account:
            raise ValueError("Account not found")

        # Check if position is sufficient
        positions = self.simulation_manager.get_positions(account_id)
        if symbol not in positions or positions[symbol].quantity < quantity:
            raise ValueError("Insufficient position")

        # Get current price
        current_price = self._get_current_price(symbol)
        total_amount = quantity * current_price
        fee = total_amount * self.transaction_fee_rate

        # Create transaction record
        transaction = VirtualTransaction(
            transaction_id=f"txn_{account_id}_{int(datetime.now().timestamp())}",
            account_id=account_id,
            symbol=symbol,
            transaction_type=TransactionType.SELL,
            order_type=order_type,
            quantity=quantity,
            price=current_price,
            total_amount=total_amount,
            fee=fee,
            timestamp=datetime.now()
        )

        # Update account balance
        account.current_balance += (total_amount - fee)
        self.simulation_manager.transactions[account_id].append(transaction)

        # Update positions
        self._update_positions(account_id)

        return transaction

    def _get_current_price(self, symbol: str) -> float:
        """Get current stock price (need to integrate StockInfoManager)"""
        # Temporary implementation, need to call StockInfoManager in practice
        return 100.0

    def _update_positions(self, account_id: str):
        """Update account positions"""
        transactions = self.simulation_manager.transactions[account_id]
        positions = {}

        # Group transactions by stock
        symbol_transactions = {}
        for txn in transactions:
            if txn.symbol not in symbol_transactions:
                symbol_transactions[txn.symbol] = []
            symbol_transactions[txn.symbol].append(txn)

        # Calculate position for each stock
        for symbol, txns in symbol_transactions.items():
            position = VirtualPosition.from_transactions(account_id, symbol, txns)
            if position and position.quantity > 0:
                positions[symbol] = position

        self.simulation_manager.positions[account_id] = positions
        self.simulation_manager.update_account_value(account_id)

class BacktestEngine:
    """Historical backtest engine"""

    def __init__(self):
        self.results = {}

    def run_backtest(self, strategy: Dict, start_date: datetime,
                    end_date: datetime, initial_balance: float = 100000.0) -> Dict[str, Any]:
        """Run historical backtest"""
        # Implement backtest logic
        # 1. Get historical data
        # 2. Execute trades according to strategy
        # 3. Calculate returns and risk metrics

        result = {
            "backtest_id": f"bt_{int(datetime.now().timestamp())}",
            "strategy": strategy,
            "period": {"start": start_date, "end": end_date},
            "initial_balance": initial_balance,
            "final_balance": initial_balance * 1.15,  # Example return
            "total_return": 15.0,
            "annualized_return": 12.5,
            "max_drawdown": -8.5,
            "sharpe_ratio": 1.2,
            "win_rate": 0.55,
            "trade_count": 45,
            "portfolio_values": [],  # Daily portfolio values
            "transactions": []       # Transaction records
        }

        return result

class PerformanceCalculator:
    """Performance calculator"""

    @staticmethod
    def calculate_returns(portfolio_values: List[float]) -> Dict[str, float]:
        """Calculate various returns"""
        if len(portfolio_values) < 2:
            return {}

        initial_value = portfolio_values[0]
        final_value = portfolio_values[-1]

        total_return = ((final_value - initial_value) / initial_value) * 100

        # Annualized return (assuming daily data)
        days = len(portfolio_values) - 1
        years = days / 365
        annualized_return = ((final_value / initial_value) ** (1 / years) - 1) * 100

        return {
            "total_return": total_return,
            "annualized_return": annualized_return
        }

    @staticmethod
    def calculate_max_drawdown(portfolio_values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(portfolio_values) < 2:
            return 0.0

        peak = portfolio_values[0]
        max_drawdown = 0.0

        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            max_drawdown = min(max_drawdown, -drawdown)

        return max_drawdown

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0

        avg_return = sum(returns) / len(returns)
        std_return = pd.Series(returns).std()

        if std_return == 0:
            return 0.0

        return (avg_return - risk_free_rate) / std_return