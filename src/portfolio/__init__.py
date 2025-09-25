"""
Portfolio Management Module for US Stock Recommendation System

This module provides comprehensive portfolio management functionality including:
- Portfolio creation and management
- Stock position tracking with weights and targets
- Portfolio analysis and performance metrics
- File-based persistence with JSON format
- Integration with existing stock analysis engine

Classes:
    Portfolio: Core portfolio data model
    Holding: Individual stock position model
    PortfolioManager: CRUD operations for portfolios
    PortfolioAnalyzer: Portfolio-level analysis
    FileManager: File persistence operations
    
Usage:
    from src.portfolio import Portfolio, PortfolioManager
    
    manager = PortfolioManager()
    portfolio = manager.create_portfolio("Tech Portfolio", "aggressive")
    manager.add_stock(portfolio.name, "AAPL", 0.3)
"""

from .models import Portfolio, Holding, StrategyType, AnalysisCache
from .file_manager import FileManager
from .manager import PortfolioManager
from .analyzer import PortfolioAnalyzer
from .exceptions import (
    PortfolioError,
    PortfolioNotFoundError,
    InvalidWeightError,
    DuplicatePortfolioError,
    FileOperationError,
    ValidationError,
    AnalysisError,
    InsufficientDataError
)

__all__ = [
    'Portfolio',
    'Holding', 
    'StrategyType',
    'AnalysisCache',
    'FileManager',
    'PortfolioManager',
    'PortfolioAnalyzer',
    'PortfolioError',
    'PortfolioNotFoundError',
    'InvalidWeightError',
    'DuplicatePortfolioError',
    'FileOperationError',
    'ValidationError',
    'AnalysisError',
    'InsufficientDataError'
]

__version__ = '1.0.0'
__author__ = 'US Stock Recommendation System'