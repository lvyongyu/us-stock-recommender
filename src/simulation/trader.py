"""
Simulation Trading System - Virtual Trading Engine
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .models import VirtualTransaction, TransactionType, OrderType, VirtualPosition
from .account_manager import SimulationAccountManager

class VirtualTrader:
    """Virtual trading engine"""

    def __init__(self, account_manager: SimulationAccountManager):
        self.account_manager = account_manager
        self.transaction_fee_rate = 0.001  # 0.1% transaction fee

    def execute_buy_order(self, account_id: str, symbol: str,
                         quantity: int, order_type: OrderType = OrderType.MARKET) -> VirtualTransaction:
        """Execute buy order"""
        account = self.account_manager.get_account(account_id)
        if not account:
            raise ValueError("Account does not exist")

        # Get current price
        current_price = self._get_current_price(symbol)
        total_amount = quantity * current_price
        fee = total_amount * self.transaction_fee_rate

        # Check if funds are sufficient
        if account.available_balance < (total_amount + fee):
            raise ValueError(f"Insufficient funds. Available balance: ${account.available_balance:.2f}, Required: ${(total_amount + fee):.2f}")

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
        self.account_manager.update_account_balance(account_id, -(total_amount + fee))

        # Add transaction record
        self.account_manager.add_transaction(transaction)

        return transaction

    def execute_sell_order(self, account_id: str, symbol: str,
                          quantity: int, order_type: OrderType = OrderType.MARKET) -> VirtualTransaction:
        """Execute sell order"""
        account = self.account_manager.get_account(account_id)
        if not account:
            raise ValueError("Account does not exist")

        # Check if position is sufficient
        positions = self.account_manager.calculate_positions(account_id)
        if symbol not in positions or positions[symbol].quantity < quantity:
            available_qty = positions.get(symbol, VirtualPosition("", "", 0, 0, 0, 0, 0, 0)).quantity
            raise ValueError(f"Insufficient position. Holding: {available_qty} shares, Selling: {quantity} shares")

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
        self.account_manager.update_account_balance(account_id, (total_amount - fee))

        # Add transaction record
        self.account_manager.add_transaction(transaction)

        return transaction

    def _get_current_price(self, symbol: str) -> float:
        """Get current stock price from real market data"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            # Get the most recent closing price
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                if current_price > 0:
                    print(f"📈 {symbol} current price: ${current_price:.2f}")
                    return current_price
        except Exception as e:
            print(f"⚠️  Error fetching real price for {symbol}: {e}, using simulated price")

        # Fallback to simulated price if real data fails
        import random
        base_price = 100.0
        simulated_price = base_price + random.uniform(-10, 10)
        print(f"🎲 {symbol} simulated price: ${simulated_price:.2f}")
        return max(simulated_price, 1.0)  # Ensure price is not negative

    def validate_order(self, account_id: str, symbol: str, quantity: int,
                      transaction_type: TransactionType) -> Dict[str, Any]:
        """Validate order"""
        account = self.account_manager.get_account(account_id)
        if not account:
            return {"valid": False, "message": "Account does not exist"}

        current_price = self._get_current_price(symbol)
        total_amount = quantity * current_price
        fee = total_amount * self.transaction_fee_rate

        if transaction_type == TransactionType.BUY:
            required_amount = total_amount + fee
            if account.available_balance < required_amount:
                return {
                    "valid": False,
                    "message": f"Insufficient funds. Required: ${required_amount:.2f}, Available: ${account.available_balance:.2f}"
                }
        else:  # SELL
            positions = self.account_manager.calculate_positions(account_id)
            if symbol not in positions or positions[symbol].quantity < quantity:
                available_qty = positions.get(symbol, VirtualPosition("", "", 0, 0, 0, 0, 0, 0)).quantity
                return {
                    "valid": False,
                    "message": f"Insufficient position. Holding: {available_qty} shares, Selling: {quantity} shares"
                }

        return {
            "valid": True,
            "message": "Order is valid",
            "estimated_cost": total_amount,
            "fee": fee,
            "total_amount": total_amount + fee if transaction_type == TransactionType.BUY else total_amount - fee
        }