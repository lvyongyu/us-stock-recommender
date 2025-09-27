"""
Simulation Trading System Data Models
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

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
                         transactions: List[VirtualTransaction]) -> Optional['VirtualPosition']:
        """Calculate position from transaction records"""
        buy_transactions = [t for t in transactions
                          if t.symbol == symbol and t.transaction_type == TransactionType.BUY]
        sell_transactions = [t for t in transactions
                           if t.symbol == symbol and t.transaction_type == TransactionType.SELL]

        total_buy_quantity = sum(t.quantity for t in buy_transactions)
        total_sell_quantity = sum(t.quantity for t in sell_transactions)
        net_quantity = total_buy_quantity - total_sell_quantity

        if net_quantity <= 0:
            return None

        # Calculate average cost (weighted average)
        total_cost = 0
        remaining_quantity = net_quantity

        # Process transactions in chronological order
        sorted_transactions = sorted(transactions, key=lambda t: t.timestamp)

        for transaction in sorted_transactions:
            if transaction.transaction_type == TransactionType.BUY:
                if remaining_quantity > 0:
                    cost_amount = min(remaining_quantity, transaction.quantity) * transaction.price
                    total_cost += cost_amount
                    remaining_quantity -= transaction.quantity
            elif transaction.transaction_type == TransactionType.SELL:
                # Sell transactions don't affect cost calculation
                pass

        if total_cost == 0:
            return None

        average_cost = total_cost / net_quantity

        # Get current price from real market data
        current_price = cls._get_current_price(symbol)

        market_value = net_quantity * current_price
        unrealized_pnl = market_value - total_cost
        unrealized_pnl_pct = (unrealized_pnl / total_cost) * 100 if total_cost > 0 else 0

        return cls(
            account_id=account_id,
            symbol=symbol,
            quantity=net_quantity,
            average_cost=average_cost,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct
        )

    @staticmethod
    def _get_current_price(symbol: str) -> float:
        """Get current stock price from real market data"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            # Get the most recent closing price
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                return current_price
        except Exception as e:
            print(f"⚠️  Error fetching real price for {symbol}: {e}, using fallback price")

        # Fallback price if real data fails
        return 100.0

@dataclass
class SimulationAccount:
    """Simulation account"""
    account_id: str
    user_id: str
    account_name: str
    initial_balance: float
    current_balance: float
    total_value: float
    total_return: float
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    @property
    def total_return_pct(self) -> float:
        """Total return percentage"""
        return ((self.total_value - self.initial_balance) / self.initial_balance) * 100

    @property
    def available_balance(self) -> float:
        """Available funds (considering position margin requirements)"""
        # Simple implementation, may need to consider margin requirements in practice
        return self.current_balance