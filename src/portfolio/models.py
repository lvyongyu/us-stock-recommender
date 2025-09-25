"""
Portfolio Management System Data Models

Core data models for portfolio management including:
- Portfolio: Main portfolio container
- Holding: Individual stock position 
- StrategyType: Investment strategy enumeration
- AnalysisCache: Cached analysis results

These models provide the foundation for all portfolio operations.
"""

import uuid
import json
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict

from .exceptions import ValidationError, InvalidWeightError


class StrategyType(Enum):
    """Investment strategy types for portfolio classification."""
    
    CONSERVATIVE = "conservative"
    BALANCED = "balanced" 
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

    @classmethod
    def from_string(cls, strategy_str: str) -> 'StrategyType':
        """Convert string to StrategyType enum."""
        try:
            return cls(strategy_str.lower())
        except ValueError:
            # Default to custom for unknown strategies
            return cls.CUSTOM

    def get_display_name(self, language: str = 'en') -> str:
        """Get localized display name for strategy."""
        display_names = {
            'en': {
                self.CONSERVATIVE: 'Conservative',
                self.BALANCED: 'Balanced',
                self.AGGRESSIVE: 'Aggressive', 
                self.CUSTOM: 'Custom'
            },
            'zh': {
                self.CONSERVATIVE: '保守型',
                self.BALANCED: '平衡型',
                self.AGGRESSIVE: '激进型',
                self.CUSTOM: '自定义'
            }
        }
        return display_names.get(language, display_names['en']).get(self, 'Unknown')


@dataclass
class AnalysisCache:
    """Cache container for portfolio analysis results."""
    
    last_analysis_time: Optional[datetime] = None
    overall_recommendation: Optional[str] = None
    confidence: Optional[float] = None
    risk_level: Optional[str] = None
    expected_return: Optional[float] = None
    diversification_score: Optional[float] = None
    rebalance_needed: Optional[bool] = None
    analysis_details: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self, max_age_minutes: int = 60) -> bool:
        """Check if cached analysis is still valid."""
        if not self.last_analysis_time:
            return False
        
        age = datetime.now() - self.last_analysis_time
        return age.total_seconds() < (max_age_minutes * 60)
    
    def clear(self):
        """Clear all cached analysis data."""
        self.last_analysis_time = None
        self.overall_recommendation = None
        self.confidence = None
        self.risk_level = None
        self.expected_return = None
        self.diversification_score = None
        self.rebalance_needed = None
        self.analysis_details.clear()


@dataclass
class Holding:
    """Individual stock position within a portfolio."""
    
    symbol: str
    weight: float
    target_weight: Optional[float] = None
    notes: str = ""
    added_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Analysis results from stock analyzer
    last_analysis: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    key_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate holding data after initialization."""
        self.symbol = self.symbol.upper().strip()
        
        if not self.symbol:
            raise ValidationError("symbol", self.symbol, "Symbol cannot be empty")
        
        if not (0.0 <= self.weight <= 1.0):
            raise ValidationError("weight", self.weight, "Weight must be between 0.0 and 1.0")
        
        if self.target_weight is not None and not (0.0 <= self.target_weight <= 1.0):
            raise ValidationError("target_weight", self.target_weight, 
                                "Target weight must be between 0.0 and 1.0")
    
    def get_weight_deviation(self) -> Optional[float]:
        """Calculate deviation from target weight."""
        if self.target_weight is None:
            return None
        return self.weight - self.target_weight
    
    def needs_rebalancing(self, threshold: float = 0.05) -> bool:
        """Check if position needs rebalancing based on threshold."""
        deviation = self.get_weight_deviation()
        if deviation is None:
            return False
        return abs(deviation) > threshold
    
    def update_analysis(self, analysis_result: Dict[str, Any]):
        """Update holding with latest analysis results."""
        self.last_analysis = analysis_result
        self.recommendation = analysis_result.get('recommendation')
        self.confidence = analysis_result.get('confidence')
        self.key_metrics = analysis_result.get('key_metrics', {})
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert holding to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['added_time'] = self.added_time.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Holding':
        """Create Holding instance from dictionary."""
        # Convert ISO strings back to datetime objects
        if isinstance(data.get('added_time'), str):
            data['added_time'] = datetime.fromisoformat(data['added_time'])
        if isinstance(data.get('last_updated'), str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        return cls(**data)


@dataclass
class Portfolio:
    """Main portfolio data model containing stock holdings and metadata."""
    
    name: str
    description: str = ""
    strategy_type: StrategyType = StrategyType.BALANCED
    
    # Unique identifier and timestamps
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_time: datetime = field(default_factory=datetime.now)
    updated_time: datetime = field(default_factory=datetime.now)
    last_analysis_time: Optional[datetime] = None
    
    # Holdings and weights
    holdings: List[Holding] = field(default_factory=list)
    cash_weight: float = 0.0
    
    # Analysis cache
    analysis_cache: AnalysisCache = field(default_factory=AnalysisCache)
    
    def __post_init__(self):
        """Validate portfolio data after initialization."""
        if not self.name.strip():
            raise ValidationError("name", self.name, "Portfolio name cannot be empty")
        
        if isinstance(self.strategy_type, str):
            self.strategy_type = StrategyType.from_string(self.strategy_type)
        
        if not (0.0 <= self.cash_weight <= 1.0):
            raise ValidationError("cash_weight", self.cash_weight,
                                "Cash weight must be between 0.0 and 1.0")
    
    @property
    def total_weight(self) -> float:
        """Calculate total weight of all holdings."""
        return sum(holding.weight for holding in self.holdings) + self.cash_weight
    
    @property
    def stock_symbols(self) -> List[str]:
        """Get list of all stock symbols in portfolio."""
        return [holding.symbol for holding in self.holdings]
    
    @property
    def holdings_count(self) -> int:
        """Get number of stock holdings (excluding cash)."""
        return len(self.holdings)
    
    def add_holding(self, symbol: str, weight: float, target_weight: Optional[float] = None,
                   notes: str = "") -> Holding:
        """Add a new holding to the portfolio."""
        # Check if symbol already exists
        existing = self.get_holding(symbol)
        if existing:
            raise ValidationError("symbol", symbol, f"Symbol {symbol} already exists in portfolio")
        
        # Create new holding
        holding = Holding(
            symbol=symbol,
            weight=weight,
            target_weight=target_weight or weight,
            notes=notes
        )
        
        self.holdings.append(holding)
        self.updated_time = datetime.now()
        self.analysis_cache.clear()
        
        return holding
    
    def remove_holding(self, symbol: str) -> bool:
        """Remove a holding from the portfolio."""
        symbol = symbol.upper().strip()
        
        for i, holding in enumerate(self.holdings):
            if holding.symbol == symbol:
                del self.holdings[i]
                self.updated_time = datetime.now()
                self.analysis_cache.clear()
                return True
        
        return False
    
    def get_holding(self, symbol: str) -> Optional[Holding]:
        """Get a specific holding by symbol."""
        symbol = symbol.upper().strip()
        
        for holding in self.holdings:
            if holding.symbol == symbol:
                return holding
        
        return None
    
    def update_weight(self, symbol: str, new_weight: float) -> bool:
        """Update the weight of a specific holding."""
        holding = self.get_holding(symbol)
        if not holding:
            return False
        
        if not (0.0 <= new_weight <= 1.0):
            raise ValidationError("weight", new_weight, "Weight must be between 0.0 and 1.0")
        
        holding.weight = new_weight
        holding.last_updated = datetime.now()
        self.updated_time = datetime.now()
        self.analysis_cache.clear()
        
        return True
    
    def validate_weights(self, tolerance: float = 0.001) -> tuple[bool, float]:
        """Validate that total weights sum to approximately 1.0."""
        total = self.total_weight
        is_valid = abs(total - 1.0) <= tolerance
        return is_valid, total
    
    def normalize_weights(self):
        """Normalize all weights to sum to 1.0."""
        total = sum(holding.weight for holding in self.holdings)
        
        if total == 0:
            raise InvalidWeightError("Cannot normalize weights when total is zero")
        
        # Normalize stock weights
        for holding in self.holdings:
            holding.weight = holding.weight / total
            holding.last_updated = datetime.now()
        
        # Reset cash weight to 0 after normalization
        self.cash_weight = 0.0
        self.updated_time = datetime.now()
        self.analysis_cache.clear()
    
    def rebalance_to_targets(self):
        """Rebalance portfolio to target weights."""
        total_target_weight = sum(
            holding.target_weight for holding in self.holdings 
            if holding.target_weight is not None
        )
        
        if total_target_weight == 0:
            raise InvalidWeightError("No target weights set for rebalancing")
        
        # Update weights to target weights, normalized
        for holding in self.holdings:
            if holding.target_weight is not None:
                holding.weight = holding.target_weight / total_target_weight
                holding.last_updated = datetime.now()
        
        self.updated_time = datetime.now()
        self.analysis_cache.clear()
    
    def get_holdings_summary(self) -> Dict[str, Any]:
        """Get summary information about all holdings."""
        return {
            'total_holdings': self.holdings_count,
            'total_weight': self.total_weight,
            'cash_weight': self.cash_weight,
            'symbols': self.stock_symbols,
            'weights_valid': self.validate_weights()[0],
            'last_updated': self.updated_time.isoformat(),
            'strategy': self.strategy_type.value
        }
    
    def clear_analysis_cache(self):
        """Clear cached analysis results."""
        self.analysis_cache.clear()
        self.last_analysis_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio to dictionary for serialization."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'strategy_type': self.strategy_type.value,
            'created_time': self.created_time.isoformat(),
            'updated_time': self.updated_time.isoformat(),
            'last_analysis_time': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'cash_weight': self.cash_weight,
            'holdings': [holding.to_dict() for holding in self.holdings],
            'analysis_cache': asdict(self.analysis_cache) if self.analysis_cache else None
        }
        
        # Convert datetime in analysis_cache if present
        if data['analysis_cache'] and data['analysis_cache']['last_analysis_time']:
            data['analysis_cache']['last_analysis_time'] = \
                self.analysis_cache.last_analysis_time.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Portfolio':
        """Create Portfolio instance from dictionary."""
        # Convert ISO strings back to datetime objects
        created_time = datetime.fromisoformat(data['created_time'])
        updated_time = datetime.fromisoformat(data['updated_time'])
        last_analysis_time = None
        if data.get('last_analysis_time'):
            last_analysis_time = datetime.fromisoformat(data['last_analysis_time'])
        
        # Convert holdings
        holdings = [Holding.from_dict(holding_data) for holding_data in data.get('holdings', [])]
        
        # Convert analysis cache
        analysis_cache = AnalysisCache()
        if data.get('analysis_cache'):
            cache_data = data['analysis_cache']
            if cache_data.get('last_analysis_time'):
                cache_data['last_analysis_time'] = datetime.fromisoformat(cache_data['last_analysis_time'])
            analysis_cache = AnalysisCache(**cache_data)
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            strategy_type=StrategyType.from_string(data.get('strategy_type', 'balanced')),
            created_time=created_time,
            updated_time=updated_time,
            last_analysis_time=last_analysis_time,
            cash_weight=data.get('cash_weight', 0.0),
            holdings=holdings,
            analysis_cache=analysis_cache
        )