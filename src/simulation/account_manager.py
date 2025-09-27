"""
Simulation Trading System - Account Management Module
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import os
from .models import SimulationAccount, VirtualTransaction, VirtualPosition

class SimulationAccountManager:
    """Simulation account manager"""

    def __init__(self, data_dir: str = "~/.stock_recommender/simulation"):
        self.data_dir = os.path.expanduser(data_dir)
        self.accounts_file = os.path.join(self.data_dir, "accounts.json")
        self.transactions_file = os.path.join(self.data_dir, "transactions.json")

        os.makedirs(self.data_dir, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Load data"""
        self.accounts = {}
        self.transactions = {}

        # Load account data
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
                for account_data in accounts_data:
                    # Ensure total_return field exists (backward compatibility)
                    if 'total_return' not in account_data:
                        account_data['total_return'] = 0.0
                    account = SimulationAccount(**account_data)
                    self.accounts[account.account_id] = account

        # Load transaction data
        if os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'r', encoding='utf-8') as f:
                self.transactions = json.load(f)

    def _save_data(self):
        """Save data"""
        # Save account data
        accounts_data = [asdict(account) for account in self.accounts.values()]
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(accounts_data, f, indent=2, default=str)

        # Save transaction data
        with open(self.transactions_file, 'w', encoding='utf-8') as f:
            json.dump(self.transactions, f, indent=2, default=str)

    def create_account(self, user_id: str, account_name: str = "Default Simulation Account",
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
            total_return=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )

        self.accounts[account_id] = account
        self.transactions[account_id] = []
        self._save_data()

        return account

    def get_account(self, account_id: str) -> Optional[SimulationAccount]:
        """Get account"""
        return self.accounts.get(account_id)

    def get_user_accounts(self, user_id: str) -> List[SimulationAccount]:
        """Get all user accounts"""
        return [account for account in self.accounts.values()
                if account.user_id == user_id and account.is_active]

    def update_account_balance(self, account_id: str, amount: float):
        """Update account balance"""
        if account_id in self.accounts:
            self.accounts[account_id].current_balance += amount
            self.accounts[account_id].updated_at = datetime.now()
            self._save_data()

    def add_transaction(self, transaction: VirtualTransaction):
        """Add transaction record"""
        account_id = transaction.account_id
        if account_id not in self.transactions:
            self.transactions[account_id] = []

        self.transactions[account_id].append(asdict(transaction))
        self._save_data()

    def get_transaction_history(self, account_id: str, limit: int = 100) -> List[VirtualTransaction]:
        """Get transaction history"""
        if account_id not in self.transactions:
            return []

        transactions_data = self.transactions[account_id][-limit:]
        transactions = []

        for txn_data in transactions_data:
            # Convert timestamp
            txn_data_copy = txn_data.copy()
            if isinstance(txn_data_copy['timestamp'], str):
                txn_data_copy['timestamp'] = datetime.fromisoformat(txn_data_copy['timestamp'])
            transactions.append(VirtualTransaction(**txn_data_copy))

        return transactions

    def calculate_positions(self, account_id: str) -> Dict[str, VirtualPosition]:
        """Calculate account positions"""
        transactions = self.get_transaction_history(account_id, limit=1000)
        if not transactions:
            return {}

        # Group by stock
        positions = {}
        for symbol in set(txn.symbol for txn in transactions):
            symbol_transactions = [t for t in transactions if t.symbol == symbol]
            position = VirtualPosition.from_transactions(account_id, symbol, symbol_transactions)
            if position and position.quantity > 0:
                positions[symbol] = position

        return positions

    def get_account_summary(self, account_id: str) -> Dict[str, Any]:
        """Get account summary"""
        account = self.get_account(account_id)
        if not account:
            return None

        positions = self.calculate_positions(account_id)
        positions_value = sum(pos.market_value for pos in positions.values())

        # Update account total value
        account.total_value = account.current_balance + positions_value

        return {
            "account": account,
            "positions": positions,
            "positions_value": positions_value,
            "total_return": account.total_return,
            "total_return_pct": account.total_return
        }

    def delete_account(self, account_id: str) -> bool:
        """Delete simulation account and all related data"""
        if account_id not in self.accounts:
            return False

        # Remove account
        del self.accounts[account_id]

        # Remove related transactions
        if account_id in self.transactions:
            del self.transactions[account_id]

        # Save changes
        self._save_data()
        return True