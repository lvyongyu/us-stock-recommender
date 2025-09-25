"""
Portfolio Management System - Portfolio Manager

Provides comprehensive CRUD (Create, Read, Update, Delete) operations for portfolios.
Handles in-memory portfolio management with file system persistence integration.

Key Features:
- Portfolio lifecycle management
- Stock holding operations 
- Weight management and validation
- Batch operations support
- Error handling and validation
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from .models import Portfolio, Holding, StrategyType
from .file_manager import FileManager
from .exceptions import (
    PortfolioNotFoundError,
    DuplicatePortfolioError,
    InvalidWeightError,
    ValidationError
)


class PortfolioManager:
    """Manages portfolio CRUD operations and in-memory storage."""
    
    def __init__(self, file_manager: FileManager = None):
        """
        Initialize portfolio manager.
        
        Args:
            file_manager: Optional custom file manager instance
        """
        self.file_manager = file_manager or FileManager()
        self.portfolios: Dict[str, Portfolio] = {}
        
        # Load existing portfolios from disk
        self._load_existing_portfolios()
    
    def _load_existing_portfolios(self):
        """Load all existing portfolios from disk into memory."""
        try:
            portfolio_files = self.file_manager.list_portfolio_files()
            
            for portfolio_name in portfolio_files:
                try:
                    file_path = self.file_manager._get_portfolio_file_path(portfolio_name)
                    portfolio = self.file_manager.load_portfolio(str(file_path))
                    self.portfolios[portfolio.name] = portfolio
                except Exception as e:
                    print(f"Warning: Failed to load portfolio '{portfolio_name}': {e}")
                    
        except Exception as e:
            print(f"Warning: Failed to load existing portfolios: {e}")
    
    def create_portfolio(self, name: str, description: str = "", 
                        strategy_type: StrategyType = StrategyType.BALANCED) -> Portfolio:
        """
        Create a new portfolio.
        
        Args:
            name: Portfolio name (must be unique)
            description: Optional portfolio description  
            strategy_type: Investment strategy type
            
        Returns:
            Portfolio: Created portfolio instance
            
        Raises:
            DuplicatePortfolioError: If portfolio name already exists
            ValidationError: If input validation fails
        """
        name = name.strip()
        
        if not name:
            raise ValidationError("name", name, "Portfolio name cannot be empty")
        
        if name in self.portfolios:
            raise DuplicatePortfolioError(name)
        
        # Convert string to StrategyType if needed
        if isinstance(strategy_type, str):
            strategy_type = StrategyType.from_string(strategy_type)
        
        # Create new portfolio
        portfolio = Portfolio(
            name=name,
            description=description.strip(),
            strategy_type=strategy_type
        )
        
        # Save to memory and disk
        self.portfolios[name] = portfolio
        self.file_manager.save_portfolio(portfolio)
        
        return portfolio
    
    def get_portfolio(self, name_or_id: str) -> Portfolio:
        """
        Get portfolio by name or ID.
        
        Args:
            name_or_id: Portfolio name or UUID
            
        Returns:
            Portfolio: Found portfolio instance
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
        """
        # First try by name
        if name_or_id in self.portfolios:
            return self.portfolios[name_or_id]
        
        # Then try by ID
        for portfolio in self.portfolios.values():
            if portfolio.id == name_or_id:
                return portfolio
        
        raise PortfolioNotFoundError(name_or_id)
    
    def list_portfolios(self) -> List[Portfolio]:
        """
        Get list of all portfolios.
        
        Returns:
            List[Portfolio]: All portfolios sorted by name
        """
        return sorted(self.portfolios.values(), key=lambda p: p.name.lower())
    
    def update_portfolio(self, name: str, description: str = None, 
                        strategy_type: StrategyType = None) -> Portfolio:
        """
        Update portfolio metadata.
        
        Args:
            name: Portfolio name
            description: Optional new description
            strategy_type: Optional new strategy type
            
        Returns:
            Portfolio: Updated portfolio instance
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
        """
        portfolio = self.get_portfolio(name)
        
        if description is not None:
            portfolio.description = description.strip()
        
        if strategy_type is not None:
            if isinstance(strategy_type, str):
                strategy_type = StrategyType.from_string(strategy_type)
            portfolio.strategy_type = strategy_type
        
        portfolio.updated_time = datetime.now()
        portfolio.analysis_cache.clear()
        
        # Save changes
        self.file_manager.save_portfolio(portfolio)
        
        return portfolio
    
    def delete_portfolio(self, name_or_id: str) -> bool:
        """
        Delete a portfolio.
        
        Args:
            name_or_id: Portfolio name or ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            portfolio = self.get_portfolio(name_or_id)
            
            # Remove from memory
            del self.portfolios[portfolio.name]
            
            # Delete file
            self.file_manager.delete_portfolio_file(portfolio.name)
            
            return True
            
        except PortfolioNotFoundError:
            return False
    
    def duplicate_portfolio(self, source_name: str, new_name: str, 
                           new_description: str = None) -> Portfolio:
        """
        Create a copy of an existing portfolio.
        
        Args:
            source_name: Name of portfolio to copy
            new_name: Name for new portfolio
            new_description: Optional description for new portfolio
            
        Returns:
            Portfolio: New portfolio copy
            
        Raises:
            PortfolioNotFoundError: If source portfolio not found
            DuplicatePortfolioError: If new name already exists
        """
        source_portfolio = self.get_portfolio(source_name)
        
        new_name = new_name.strip()
        if new_name in self.portfolios:
            raise DuplicatePortfolioError(new_name)
        
        # Create new portfolio with copied data
        new_portfolio = Portfolio(
            name=new_name,
            description=new_description or f"Copy of {source_portfolio.name}",
            strategy_type=source_portfolio.strategy_type,
            cash_weight=source_portfolio.cash_weight
        )
        
        # Copy holdings
        for holding in source_portfolio.holdings:
            new_holding = Holding(
                symbol=holding.symbol,
                weight=holding.weight,
                target_weight=holding.target_weight,
                notes=holding.notes
            )
            new_portfolio.holdings.append(new_holding)
        
        # Save new portfolio
        self.portfolios[new_name] = new_portfolio
        self.file_manager.save_portfolio(new_portfolio)
        
        return new_portfolio
    
    def add_stock(self, portfolio_name: str, symbol: str, weight: float, 
                  target_weight: Optional[float] = None, notes: str = "") -> Holding:
        """
        Add a stock to portfolio.
        
        Args:
            portfolio_name: Target portfolio name
            symbol: Stock symbol
            weight: Position weight (0.0-1.0)
            target_weight: Optional target weight
            notes: Optional notes
            
        Returns:
            Holding: Created holding instance
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
            ValidationError: If stock already exists or validation fails
        """
        portfolio = self.get_portfolio(portfolio_name)
        holding = portfolio.add_holding(symbol, weight, target_weight, notes)
        
        # Save changes
        self.file_manager.save_portfolio(portfolio)
        
        return holding
    
    def remove_stock(self, portfolio_name: str, symbol: str) -> bool:
        """
        Remove a stock from portfolio.
        
        Args:
            portfolio_name: Target portfolio name
            symbol: Stock symbol to remove
            
        Returns:
            bool: True if removed, False if not found
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
        """
        portfolio = self.get_portfolio(portfolio_name)
        removed = portfolio.remove_holding(symbol)
        
        if removed:
            # Save changes
            self.file_manager.save_portfolio(portfolio)
        
        return removed
    
    def update_stock_weight(self, portfolio_name: str, symbol: str, 
                           new_weight: float, update_target: bool = False) -> bool:
        """
        Update weight of a specific stock.
        
        Args:
            portfolio_name: Target portfolio name
            symbol: Stock symbol
            new_weight: New weight value
            update_target: Whether to also update target weight
            
        Returns:
            bool: True if updated, False if stock not found
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
            ValidationError: If weight is invalid
        """
        portfolio = self.get_portfolio(portfolio_name)
        updated = portfolio.update_weight(symbol, new_weight)
        
        if updated and update_target:
            holding = portfolio.get_holding(symbol)
            if holding:
                holding.target_weight = new_weight
                holding.last_updated = datetime.now()
        
        if updated:
            # Save changes
            self.file_manager.save_portfolio(portfolio)
        
        return updated
    
    def add_stocks_batch(self, portfolio_name: str, 
                        stocks_data: List[Tuple[str, float, Optional[float]]]) -> List[Holding]:
        """
        Add multiple stocks to portfolio in batch.
        
        Args:
            portfolio_name: Target portfolio name
            stocks_data: List of (symbol, weight, target_weight) tuples
            
        Returns:
            List[Holding]: Created holding instances
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
            ValidationError: If any validation fails
        """
        portfolio = self.get_portfolio(portfolio_name)
        created_holdings = []
        
        for symbol, weight, target_weight in stocks_data:
            holding = portfolio.add_holding(symbol, weight, target_weight)
            created_holdings.append(holding)
        
        # Save changes once after all additions
        self.file_manager.save_portfolio(portfolio)
        
        return created_holdings
    
    def update_weights_batch(self, portfolio_name: str, 
                            weight_updates: Dict[str, float]) -> List[str]:
        """
        Update multiple stock weights in batch.
        
        Args:
            portfolio_name: Target portfolio name
            weight_updates: Dict of {symbol: new_weight}
            
        Returns:
            List[str]: Symbols that were successfully updated
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
        """
        portfolio = self.get_portfolio(portfolio_name)
        updated_symbols = []
        
        for symbol, new_weight in weight_updates.items():
            if portfolio.update_weight(symbol, new_weight):
                updated_symbols.append(symbol)
        
        # Save changes once after all updates
        if updated_symbols:
            self.file_manager.save_portfolio(portfolio)
        
        return updated_symbols
    
    def rebalance_portfolio(self, portfolio_name: str, method: str = 'target') -> Portfolio:
        """
        Rebalance portfolio weights.
        
        Args:
            portfolio_name: Target portfolio name
            method: Rebalancing method ('target', 'equal', 'normalize')
            
        Returns:
            Portfolio: Rebalanced portfolio
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
            InvalidWeightError: If rebalancing fails
        """
        portfolio = self.get_portfolio(portfolio_name)
        
        if method == 'target':
            portfolio.rebalance_to_targets()
        elif method == 'equal':
            self._rebalance_equal_weights(portfolio)
        elif method == 'normalize':
            portfolio.normalize_weights()
        else:
            raise ValidationError("method", method, f"Unknown rebalancing method: {method}")
        
        # Save changes
        self.file_manager.save_portfolio(portfolio)
        
        return portfolio
    
    def _rebalance_equal_weights(self, portfolio: Portfolio):
        """Rebalance portfolio to equal weights."""
        if not portfolio.holdings:
            return
        
        equal_weight = 1.0 / len(portfolio.holdings)
        
        for holding in portfolio.holdings:
            holding.weight = equal_weight
            holding.target_weight = equal_weight
            holding.last_updated = datetime.now()
        
        portfolio.cash_weight = 0.0
        portfolio.updated_time = datetime.now()
        portfolio.analysis_cache.clear()
    
    def validate_all_portfolios(self) -> Dict[str, List[str]]:
        """
        Validate all portfolios and return issues.
        
        Returns:
            Dict[str, List[str]]: Dict of {portfolio_name: [issues]}
        """
        validation_results = {}
        
        for name, portfolio in self.portfolios.items():
            issues = []
            
            # Check weight validation
            is_valid, total_weight = portfolio.validate_weights()
            if not is_valid:
                issues.append(f"Invalid total weight: {total_weight:.3f} (should be 1.0)")
            
            # Check for duplicate symbols
            symbols = [h.symbol for h in portfolio.holdings]
            if len(symbols) != len(set(symbols)):
                issues.append("Duplicate symbols found")
            
            # Check for empty holdings
            if not portfolio.holdings and portfolio.cash_weight == 0:
                issues.append("Portfolio has no holdings")
            
            if issues:
                validation_results[name] = issues
        
        return validation_results
    
    def get_portfolio_summary(self, portfolio_name: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of a portfolio.
        
        Args:
            portfolio_name: Portfolio name
            
        Returns:
            Dict containing portfolio summary information
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
        """
        portfolio = self.get_portfolio(portfolio_name)
        
        holdings_info = []
        for holding in portfolio.holdings:
            holdings_info.append({
                'symbol': holding.symbol,
                'weight': holding.weight,
                'target_weight': holding.target_weight,
                'deviation': holding.get_weight_deviation(),
                'needs_rebalancing': holding.needs_rebalancing(),
                'recommendation': holding.recommendation,
                'confidence': holding.confidence,
                'notes': holding.notes,
                'last_updated': holding.last_updated.isoformat()
            })
        
        return {
            'basic_info': {
                'id': portfolio.id,
                'name': portfolio.name,
                'description': portfolio.description,
                'strategy': portfolio.strategy_type.value,
                'created_time': portfolio.created_time.isoformat(),
                'updated_time': portfolio.updated_time.isoformat()
            },
            'holdings_summary': portfolio.get_holdings_summary(),
            'holdings_detail': holdings_info,
            'validation': {
                'weights_valid': portfolio.validate_weights()[0],
                'total_weight': portfolio.total_weight,
                'rebalancing_needed': any(h.needs_rebalancing() for h in portfolio.holdings)
            },
            'analysis_cache': {
                'has_cached_analysis': portfolio.analysis_cache.is_valid(),
                'last_analysis_time': portfolio.last_analysis_time.isoformat() if portfolio.last_analysis_time else None,
                'overall_recommendation': portfolio.analysis_cache.overall_recommendation,
                'risk_level': portfolio.analysis_cache.risk_level
            }
        }
    
    def export_portfolio(self, portfolio_name: str, file_path: str, format: str = 'json') -> str:
        """
        Export portfolio to file.
        
        Args:
            portfolio_name: Portfolio to export
            file_path: Target file path
            format: Export format ('json', 'csv')
            
        Returns:
            str: Path to exported file
            
        Raises:
            PortfolioNotFoundError: If portfolio not found
        """
        portfolio = self.get_portfolio(portfolio_name)
        
        if format.lower() == 'json':
            return self.file_manager.save_portfolio(portfolio, file_path)
        elif format.lower() == 'csv':
            return self.file_manager.export_to_csv(portfolio, file_path)
        else:
            raise ValidationError("format", format, f"Unsupported export format: {format}")
    
    def import_portfolio_from_file(self, file_path: str) -> Portfolio:
        """
        Import portfolio from file.
        
        Args:
            file_path: Path to portfolio file
            
        Returns:
            Portfolio: Imported portfolio
            
        Raises:
            DuplicatePortfolioError: If portfolio name already exists
        """
        portfolio = self.file_manager.load_portfolio(file_path)
        
        if portfolio.name in self.portfolios:
            raise DuplicatePortfolioError(portfolio.name)
        
        # Add to memory
        self.portfolios[portfolio.name] = portfolio
        
        return portfolio