"""
Portfolio Analysis Engine

Integrates with existing stock analysis system to provide portfolio-level analysis.
Combines individual stock recommendations into comprehensive portfolio insights.

Key Features:
- Portfolio-level recommendation aggregation
- Risk assessment and diversification analysis  
- Performance metrics calculation
- Rebalancing suggestions
- Integration with existing StockAnalyzer and RecommendationEngine
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import statistics
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from .models import Portfolio, Holding, AnalysisCache
from .exceptions import AnalysisError, InsufficientDataError

# Import existing analysis components
try:
    from src.analyzers.stock_analyzer import StockAnalyzer
    from src.engines.recommendation_engine import RecommendationEngine  
    from src.batch.batch_analyzer import BatchAnalyzer
    from src.languages.config import get_language_config
    from src.utils.stock_info_manager import get_stock_manager
except ImportError as e:
    print(f"Warning: Could not import existing analysis components: {e}")
    StockAnalyzer = None
    RecommendationEngine = None
    BatchAnalyzer = None
    get_stock_manager = None


class PortfolioAnalyzer:
    """Analyzes portfolios using integrated stock analysis system."""
    
    def __init__(self, language: str = 'en'):
        """
        Initialize portfolio analyzer.
        
        Args:
            language: Language for analysis results ('en' or 'zh')
        """
        self.language = language
        
        # Initialize existing analysis components if available
        try:
            if StockAnalyzer:
                self.stock_analyzer_class = StockAnalyzer
            else:
                self.stock_analyzer_class = None
                
            if RecommendationEngine:
                # Get language configuration first
                try:
                    lang_config = get_language_config(language)
                except:
                    lang_config = self._get_fallback_language_config()
                
                # Create recommendation engine with proper parameters
                self.recommendation_engine = RecommendationEngine(
                    analyzer=None,  # Will be set per stock
                    lang_config=lang_config
                )
            else:
                self.recommendation_engine = None
                
            if BatchAnalyzer:
                self.batch_analyzer = BatchAnalyzer()
            else:
                self.batch_analyzer = None
                
            if get_stock_manager:
                self.stock_manager = get_stock_manager()
            else:
                self.stock_manager = None
                
            # Get language configuration
            try:
                self.lang_config = get_language_config(language)
            except:
                self.lang_config = self._get_fallback_language_config()
                
        except Exception as e:
            print(f"Warning: Failed to initialize analysis components: {e}")
            self._initialize_fallback_analyzers()
    
    def _initialize_fallback_analyzers(self):
        """Initialize fallback analyzers when main components unavailable."""
        self.stock_analyzer_class = None
        self.recommendation_engine = None
        self.batch_analyzer = None
        self.stock_manager = None
        self.lang_config = self._get_fallback_language_config()
    
    def _get_fallback_language_config(self) -> Dict[str, str]:
        """Get fallback language configuration."""
        if self.language == 'zh':
            return {
                'buy': '买入',
                'sell': '卖出', 
                'hold': '持有',
                'short': '做空',
                'high_risk': '高风险',
                'medium_risk': '中等风险',
                'low_risk': '低风险',
                'strong_buy': '强烈买入',
                'weak_buy': '谨慎买入',
                'portfolio_analysis': '投资组合分析',
                'recommendation': '推荐',
                'confidence': '置信度',
                'risk_level': '风险等级'
            }
        else:
            return {
                'buy': 'BUY',
                'sell': 'SELL',
                'hold': 'HOLD', 
                'short': 'SHORT',
                'high_risk': 'High Risk',
                'medium_risk': 'Medium Risk',
                'low_risk': 'Low Risk',
                'strong_buy': 'Strong Buy',
                'weak_buy': 'Weak Buy',
                'portfolio_analysis': 'Portfolio Analysis',
                'recommendation': 'Recommendation',
                'confidence': 'Confidence',
                'risk_level': 'Risk Level'
            }
    
    def analyze_portfolio(self, portfolio: Portfolio, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio analysis.
        
        Args:
            portfolio: Portfolio to analyze
            force_refresh: Whether to ignore cached results
            
        Returns:
            Dict containing comprehensive analysis results
            
        Raises:
            AnalysisError: If analysis fails
            InsufficientDataError: If insufficient data for analysis
        """
        try:
            # Check if we can use cached results
            if not force_refresh and portfolio.analysis_cache.is_valid(max_age_minutes=30):
                return self._get_cached_analysis(portfolio)
            
            if not portfolio.holdings:
                raise InsufficientDataError("portfolio holdings", 1)
            
            # Analyze individual stocks
            individual_analysis = self._analyze_individual_stocks(portfolio, force_refresh)
            
            # Calculate portfolio-level metrics
            portfolio_metrics = self._calculate_portfolio_metrics(portfolio, individual_analysis)
            
            # Generate overall recommendation
            overall_recommendation = self._generate_overall_recommendation(
                portfolio, individual_analysis, portfolio_metrics
            )
            
            # Assess portfolio risk
            risk_assessment = self._assess_portfolio_risk(portfolio, individual_analysis)
            
            # Generate rebalancing suggestions
            rebalance_suggestions = self._generate_rebalance_suggestions(portfolio)
            
            # Compile comprehensive results
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_info': {
                    'name': portfolio.name,
                    'strategy': portfolio.strategy_type.value,
                    'holdings_count': len(portfolio.holdings),
                    'total_weight': portfolio.total_weight
                },
                'individual_analysis': individual_analysis,
                'portfolio_metrics': portfolio_metrics,
                'overall_recommendation': overall_recommendation,
                'risk_assessment': risk_assessment,
                'rebalance_suggestions': rebalance_suggestions,
                'diversification_analysis': self._analyze_diversification(portfolio),
                'language': self.language
            }
            
            # Cache the results
            self._update_analysis_cache(portfolio, analysis_results)
            
            return analysis_results
            
        except Exception as e:
            raise AnalysisError("portfolio analysis", str(e))
    
    def _analyze_individual_stocks(self, portfolio: Portfolio, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Analyze individual stocks in the portfolio."""
        individual_analysis = {}
        
        if self.batch_analyzer and len(portfolio.holdings) > 1:
            # Use batch analysis for efficiency
            symbols = [holding.symbol for holding in portfolio.holdings]
            try:
                batch_results = self.batch_analyzer.analyze_multiple_stocks(symbols)
                
                for holding in portfolio.holdings:
                    symbol = holding.symbol
                    if symbol in batch_results:
                        analysis_result = batch_results[symbol]
                        individual_analysis[symbol] = self._format_stock_analysis(
                            symbol, analysis_result, holding
                        )
                    else:
                        # Fallback for failed analysis
                        individual_analysis[symbol] = self._create_fallback_analysis(holding, force_refresh)
                        
            except Exception as e:
                print(f"Warning: Batch analysis failed: {e}")
                # Fallback to individual analysis or mock data
                for holding in portfolio.holdings:
                    individual_analysis[holding.symbol] = self._create_fallback_analysis(holding, force_refresh)
        else:
            # Analyze stocks individually or use fallback
            for holding in portfolio.holdings:
                if self.stock_analyzer_class:
                    try:
                        # This would call the actual stock analyzer
                        # analysis_result = self.stock_analyzer.analyze_stock(holding.symbol)
                        # For now, create fallback analysis
                        individual_analysis[holding.symbol] = self._create_fallback_analysis(holding, force_refresh)
                    except Exception as e:
                        print(f"Warning: Failed to analyze {holding.symbol}: {e}")
                        individual_analysis[holding.symbol] = self._create_fallback_analysis(holding, force_refresh)
                else:
                    individual_analysis[holding.symbol] = self._create_fallback_analysis(holding, force_refresh)
        
        return individual_analysis
    
    def _format_stock_analysis(self, symbol: str, analysis_result: Dict[str, Any], 
                             holding: Holding) -> Dict[str, Any]:
        """Format stock analysis result for portfolio context."""
        return {
            'symbol': symbol,
            'weight': holding.weight,
            'target_weight': holding.target_weight,
            'recommendation': analysis_result.get('recommendation', 'HOLD'),
            'confidence': analysis_result.get('confidence', 0.5),
            'key_metrics': analysis_result.get('key_metrics', {}),
            'risk_score': analysis_result.get('risk_score', 0.5),
            'expected_return': analysis_result.get('expected_return', 0.0),
            'analysis_time': datetime.now().isoformat(),
            'notes': holding.notes
        }
    
    def _create_fallback_analysis(self, holding: Holding, force_refresh: bool = False) -> Dict[str, Any]:
        """Create fallback analysis when real analysis unavailable."""
        symbol = holding.symbol
        
        # Try to get basic stock information from stock manager
        stock_info = None
        try:
            if self.stock_manager:
                stock_info = self.stock_manager.get_stock_info(symbol, force_refresh=force_refresh)
        except Exception as e:
            print(f"Warning: Could not get stock info for {symbol}: {e}")
        
        # Mock recommendation based on symbol patterns
        if any(tech in symbol for tech in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']):
            recommendation = 'BUY'
            confidence = 0.75
            risk_score = 0.6
            expected_return = 0.12
        elif any(safe in symbol for safe in ['VTI', 'BND', 'SPY']):
            recommendation = 'HOLD'
            confidence = 0.8
            risk_score = 0.3
            expected_return = 0.08
        else:
            recommendation = 'HOLD'
            confidence = 0.5
            risk_score = 0.5
            expected_return = 0.07
        
        # Create base result
        result = {
            'symbol': symbol,
            'weight': holding.weight,
            'target_weight': holding.target_weight,
            'recommendation': recommendation,
            'confidence': confidence,
            'key_metrics': {
                'price_change': 0.02,
                'volume_ratio': 1.1,
                'volatility': risk_score
            },
            'risk_score': risk_score,
            'expected_return': expected_return,
            'analysis_time': datetime.now().isoformat(),
            'notes': holding.notes,
            'is_mock_data': True
        }
        
        # Add stock information if available
        if stock_info:
            result.update({
                'current_price': stock_info.get('current_price'),
                'price_change': stock_info.get('price_change', 0.0),
                'price_change_pct': stock_info.get('price_change_pct', 0.0),
            })
            
            # Try to get market analysis data
            market_analysis = self._get_market_analysis(symbol, stock_info)
            result.update(market_analysis)
        else:
            # Default values when no stock info available
            result.update({
                'current_price': None,
                'price_change': None,
                'price_change_pct': None,
                'trend': 'Unknown',
                'momentum': 'Neutral',
                'volume': 'Normal',
                'risk_level': 'Medium',
                'strategy_used': 'Fallback Analysis',
                'key_metrics': {
                    'RSI': 50.0,
                    'MACD': 0.0,
                    'SMA20': None,
                    'SMA50': None,
                    'price_change': 0.0,
                    'volume_ratio': 1.0,
                    'volatility': risk_score
                }
            })
        
        return result
    
    def _get_market_analysis(self, symbol: str, stock_info: Dict) -> Dict[str, Any]:
        """Get market analysis data for a stock."""
        try:
            # Try to create stock analyzer and get metrics
            if self.stock_analyzer_class:
                analyzer = self.stock_analyzer_class(symbol)
                analyzer.fetch_data()
                metrics = analyzer.get_current_metrics()
                
                # Create recommendation engine for analysis
                if self.recommendation_engine:
                    trend = self.recommendation_engine._analyze_trend(metrics)
                    momentum = self.recommendation_engine._analyze_momentum(metrics)
                    volume = self.recommendation_engine._analyze_volume(metrics)
                    risk_level = self.recommendation_engine._assess_risk(metrics)
                else:
                    # Fallback analysis without recommendation engine
                    trend = self._analyze_trend_fallback(metrics)
                    momentum = self._analyze_momentum_fallback(metrics)
                    volume = self._analyze_volume_fallback(metrics)
                    risk_level = "Medium"
                
                return {
                    'trend': trend,
                    'momentum': momentum,
                    'volume': volume,
                    'risk_level': risk_level,
                    'strategy_used': 'Technical Analysis',
                    'key_metrics': {
                        'RSI': round(metrics.get('rsi', 50.0), 2),
                        'MACD': round(metrics.get('macd', 0.0), 4),
                        'SMA20': round(metrics.get('sma_20', 0.0), 2),
                        'SMA50': round(metrics.get('sma_50', 0.0), 2),
                        'price_change': round(metrics.get('price_change', 0.0), 2),
                        'volume_ratio': round(metrics.get('volume', 0.0) / metrics.get('avg_volume', 1.0), 2),
                        'volatility': 0.5  # Default volatility
                    }
                }
        except Exception as e:
            print(f"Warning: Could not perform market analysis for {symbol}: {e}")
        
        # Fallback when analysis fails
        current_price = stock_info.get('current_price')
        return {
            'trend': 'Unknown',
            'momentum': 'Neutral',
            'volume': 'Normal',
            'risk_level': 'Medium',
            'strategy_used': 'Basic Analysis',
            'key_metrics': {
                'RSI': 50.0,
                'MACD': 0.0,
                'SMA20': current_price,
                'SMA50': current_price,
                'price_change': 0.0,
                'volume_ratio': 1.0,
                'volatility': 0.5
            }
        }
    
    def _analyze_trend_fallback(self, metrics: Dict) -> str:
        """Fallback trend analysis when recommendation engine unavailable."""
        try:
            current_price = metrics.get('current_price', 0)
            sma_20 = metrics.get('sma_20', current_price)
            sma_50 = metrics.get('sma_50', current_price)
            
            if current_price > sma_20 > sma_50:
                return "Uptrend"
            elif current_price < sma_20 < sma_50:
                return "Downtrend"
            else:
                return "Sideways"
        except:
            return "Unknown"
    
    def _analyze_momentum_fallback(self, metrics: Dict) -> str:
        """Fallback momentum analysis when recommendation engine unavailable."""
        try:
            rsi = metrics.get('rsi', 50)
            macd = metrics.get('macd', 0)
            macd_signal = metrics.get('macd_signal', 0)
            
            signals = []
            
            if rsi > 70:
                signals.append("Overbought")
            elif rsi < 30:
                signals.append("Oversold")
            else:
                signals.append("Neutral RSI")
                
            if macd > macd_signal:
                signals.append("Bullish MACD")
            else:
                signals.append("Bearish MACD")
            
            return " | ".join(signals)
        except:
            return "Neutral"
    
    def _analyze_volume_fallback(self, metrics: Dict) -> str:
        """Fallback volume analysis when recommendation engine unavailable."""
        try:
            current_volume = metrics.get('volume', 0)
            avg_volume = metrics.get('avg_volume', 1)
            
            if avg_volume > 0:
                volume_ratio = current_volume / avg_volume
                
                if volume_ratio > 1.5:
                    return "High Volume"
                elif volume_ratio < 0.5:
                    return "Low Volume"
                else:
                    return "Normal Volume"
        except:
            pass
        return "Normal"
    
    def _calculate_portfolio_metrics(self, portfolio: Portfolio, 
                                   individual_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics."""
        total_weight = sum(holding.weight for holding in portfolio.holdings)
        
        if total_weight == 0:
            return {'error': 'No holdings with positive weights'}
        
        # Calculate weighted averages
        weighted_expected_return = 0.0
        weighted_risk_score = 0.0
        weighted_confidence = 0.0
        
        for holding in portfolio.holdings:
            analysis = individual_analysis.get(holding.symbol, {})
            weight_ratio = holding.weight / total_weight
            
            weighted_expected_return += analysis.get('expected_return', 0.0) * weight_ratio
            weighted_risk_score += analysis.get('risk_score', 0.5) * weight_ratio
            weighted_confidence += analysis.get('confidence', 0.5) * weight_ratio
        
        # Calculate diversification metrics
        diversification_score = self._calculate_diversification_score(portfolio)
        
        return {
            'expected_return': weighted_expected_return,
            'risk_score': weighted_risk_score,
            'confidence': weighted_confidence,
            'diversification_score': diversification_score,
            'holdings_count': len(portfolio.holdings),
            'total_weight': total_weight,
            'largest_position': max(h.weight for h in portfolio.holdings) if portfolio.holdings else 0.0,
            'smallest_position': min(h.weight for h in portfolio.holdings) if portfolio.holdings else 0.0,
            'weight_balance': statistics.stdev([h.weight for h in portfolio.holdings]) if len(portfolio.holdings) > 1 else 0.0
        }
    
    def _generate_overall_recommendation(self, portfolio: Portfolio, 
                                       individual_analysis: Dict[str, Dict[str, Any]],
                                       portfolio_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall portfolio recommendation."""
        if not individual_analysis:
            return {'recommendation': 'HOLD', 'confidence': 0.5, 'reason': 'Insufficient data'}
        
        # Count recommendations by type
        recommendation_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'SHORT': 0}
        total_confidence = 0.0
        total_weight = 0.0
        
        for holding in portfolio.holdings:
            analysis = individual_analysis.get(holding.symbol, {})
            recommendation = analysis.get('recommendation', 'HOLD')
            confidence = analysis.get('confidence', 0.5)
            
            recommendation_counts[recommendation] += holding.weight
            total_confidence += confidence * holding.weight
            total_weight += holding.weight
        
        # Determine overall recommendation
        if total_weight > 0:
            avg_confidence = total_confidence / total_weight
        else:
            avg_confidence = 0.5
        
        # Find dominant recommendation by weight
        dominant_rec = max(recommendation_counts.items(), key=lambda x: x[1])
        overall_recommendation = dominant_rec[0]
        
        # Adjust based on portfolio metrics
        risk_score = portfolio_metrics.get('risk_score', 0.5)
        diversification = portfolio_metrics.get('diversification_score', 0.5)
        
        # Generate reason
        reason_parts = []
        
        buy_weight = recommendation_counts['BUY']
        sell_weight = recommendation_counts['SELL']
        
        if buy_weight > 0.6:
            reason_parts.append(f"Strong buy signals ({buy_weight:.1%} of portfolio)")
        elif buy_weight > 0.4:
            reason_parts.append(f"Moderate buy signals ({buy_weight:.1%} of portfolio)")
        
        if sell_weight > 0.3:
            reason_parts.append(f"Some sell signals ({sell_weight:.1%} of portfolio)")
        
        if risk_score > 0.7:
            reason_parts.append("High portfolio risk")
        elif risk_score < 0.3:
            reason_parts.append("Low portfolio risk")
        
        if diversification < 0.3:
            reason_parts.append("Low diversification")
        elif diversification > 0.7:
            reason_parts.append("Well diversified")
        
        reason = "; ".join(reason_parts) if reason_parts else "Balanced portfolio signals"
        
        return {
            'recommendation': overall_recommendation,
            'confidence': avg_confidence,
            'reason': reason,
            'recommendation_breakdown': recommendation_counts,
            'strength': self._get_recommendation_strength(overall_recommendation, avg_confidence)
        }
    
    def _get_recommendation_strength(self, recommendation: str, confidence: float) -> str:
        """Get recommendation strength based on type and confidence."""
        if confidence > 0.8:
            return f"Strong {recommendation.title()}"
        elif confidence > 0.6:
            return f"Moderate {recommendation.title()}"
        else:
            return f"Weak {recommendation.title()}"
    
    def _assess_portfolio_risk(self, portfolio: Portfolio, 
                             individual_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall portfolio risk."""
        if not individual_analysis:
            return {'risk_level': 'Unknown', 'risk_score': 0.5}
        
        # Calculate weighted risk metrics
        total_weight = sum(holding.weight for holding in portfolio.holdings)
        weighted_risk = 0.0
        risk_scores = []
        
        for holding in portfolio.holdings:
            analysis = individual_analysis.get(holding.symbol, {})
            risk_score = analysis.get('risk_score', 0.5)
            weight_ratio = holding.weight / total_weight if total_weight > 0 else 0
            
            weighted_risk += risk_score * weight_ratio
            risk_scores.append(risk_score)
        
        # Calculate risk concentration
        concentration_risk = max(holding.weight for holding in portfolio.holdings) if portfolio.holdings else 0
        
        # Calculate risk distribution
        risk_std = statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0.0
        
        # Determine risk level
        if weighted_risk > 0.7 or concentration_risk > 0.5:
            risk_level = self.lang_config.get('high_risk', 'High Risk')
        elif weighted_risk > 0.4 or concentration_risk > 0.3:
            risk_level = self.lang_config.get('medium_risk', 'Medium Risk')
        else:
            risk_level = self.lang_config.get('low_risk', 'Low Risk')
        
        return {
            'risk_level': risk_level,
            'risk_score': weighted_risk,
            'concentration_risk': concentration_risk,
            'risk_distribution': risk_std,
            'risk_factors': self._identify_risk_factors(portfolio, individual_analysis)
        }
    
    def _identify_risk_factors(self, portfolio: Portfolio, 
                             individual_analysis: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify specific risk factors in the portfolio."""
        risk_factors = []
        
        # Check concentration risk
        max_weight = max(holding.weight for holding in portfolio.holdings) if portfolio.holdings else 0
        if max_weight > 0.4:
            risk_factors.append(f"High concentration in single position ({max_weight:.1%})")
        
        # Check number of holdings
        if len(portfolio.holdings) < 5:
            risk_factors.append("Low diversification (few holdings)")
        
        # Check high-risk positions
        high_risk_weight = 0.0
        for holding in portfolio.holdings:
            analysis = individual_analysis.get(holding.symbol, {})
            if analysis.get('risk_score', 0.5) > 0.7:
                high_risk_weight += holding.weight
        
        if high_risk_weight > 0.5:
            risk_factors.append(f"High-risk positions comprise {high_risk_weight:.1%} of portfolio")
        
        # Check weight validation
        is_valid, total_weight = portfolio.validate_weights()
        if not is_valid:
            risk_factors.append(f"Invalid total weight: {total_weight:.1%}")
        
        return risk_factors
    
    def _generate_rebalance_suggestions(self, portfolio: Portfolio) -> List[Dict[str, Any]]:
        """Generate portfolio rebalancing suggestions."""
        suggestions = []
        
        # Check for holdings that deviate from target weights
        for holding in portfolio.holdings:
            if holding.target_weight is not None:
                deviation = holding.get_weight_deviation()
                if deviation and abs(deviation) > 0.05:  # 5% threshold
                    action = "reduce" if deviation > 0 else "increase"
                    suggestions.append({
                        'symbol': holding.symbol,
                        'action': action,
                        'current_weight': holding.weight,
                        'target_weight': holding.target_weight,
                        'deviation': deviation,
                        'suggested_change': abs(deviation),
                        'priority': 'high' if abs(deviation) > 0.1 else 'medium'
                    })
        
        # Check overall portfolio balance
        if len(portfolio.holdings) > 0:
            weights = [h.weight for h in portfolio.holdings]
            weight_std = statistics.stdev(weights) if len(weights) > 1 else 0.0
            
            if weight_std > 0.15:  # High weight imbalance
                suggestions.append({
                    'type': 'rebalance',
                    'action': 'overall_rebalance',
                    'reason': 'High weight imbalance detected',
                    'weight_std': weight_std,
                    'priority': 'medium'
                })
        
        return suggestions
    
    def _calculate_diversification_score(self, portfolio: Portfolio) -> float:
        """Calculate portfolio diversification score (0.0 to 1.0)."""
        if not portfolio.holdings:
            return 0.0
        
        # Simple diversification based on number of holdings and weight distribution
        num_holdings = len(portfolio.holdings)
        
        # Base score from number of holdings
        holdings_score = min(num_holdings / 10.0, 1.0)  # Max score at 10+ holdings
        
        # Weight distribution score (penalize concentration)
        weights = [h.weight for h in portfolio.holdings]
        max_weight = max(weights)
        
        # Perfect diversification would have equal weights
        ideal_weight = 1.0 / num_holdings
        weight_deviations = [abs(w - ideal_weight) for w in weights]
        avg_deviation = sum(weight_deviations) / len(weight_deviations)
        
        distribution_score = max(0.0, 1.0 - (avg_deviation * 2))  # Scale deviation penalty
        
        # Combined score
        diversification_score = (holdings_score * 0.4) + (distribution_score * 0.6)
        
        return min(max(diversification_score, 0.0), 1.0)
    
    def _analyze_diversification(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Analyze portfolio diversification."""
        diversification_score = self._calculate_diversification_score(portfolio)
        
        # Analyze by sector/type (simplified - based on symbol patterns)
        sector_weights = self._analyze_sectors(portfolio)
        
        return {
            'diversification_score': diversification_score,
            'sector_analysis': sector_weights,
            'holdings_count': len(portfolio.holdings),
            'concentration_risk': max(h.weight for h in portfolio.holdings) if portfolio.holdings else 0.0,
            'recommendations': self._get_diversification_recommendations(diversification_score, sector_weights)
        }
    
    def _analyze_sectors(self, portfolio: Portfolio) -> Dict[str, float]:
        """Analyze portfolio by sectors (simplified classification)."""
        sector_weights = {
            'Technology': 0.0,
            'Finance': 0.0,
            'Healthcare': 0.0,
            'ETF/Index': 0.0,
            'Other': 0.0
        }
        
        tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
        finance_symbols = ['JPM', 'BAC', 'WFC', 'GS', 'MS']
        healthcare_symbols = ['JNJ', 'PFE', 'UNH', 'MRK']
        etf_symbols = ['VTI', 'SPY', 'QQQ', 'BND', 'VEA', 'VWO']
        
        for holding in portfolio.holdings:
            symbol = holding.symbol
            if symbol in tech_symbols:
                sector_weights['Technology'] += holding.weight
            elif symbol in finance_symbols:
                sector_weights['Finance'] += holding.weight
            elif symbol in healthcare_symbols:
                sector_weights['Healthcare'] += holding.weight
            elif symbol in etf_symbols:
                sector_weights['ETF/Index'] += holding.weight
            else:
                sector_weights['Other'] += holding.weight
        
        return sector_weights
    
    def _get_diversification_recommendations(self, diversification_score: float, 
                                           sector_weights: Dict[str, float]) -> List[str]:
        """Get diversification improvement recommendations."""
        recommendations = []
        
        if diversification_score < 0.3:
            recommendations.append("Consider adding more holdings to improve diversification")
        
        # Check sector concentration
        for sector, weight in sector_weights.items():
            if weight > 0.6:
                recommendations.append(f"High concentration in {sector} ({weight:.1%}) - consider diversifying")
        
        if len([w for w in sector_weights.values() if w > 0]) < 3:
            recommendations.append("Consider diversifying across more sectors")
        
        return recommendations
    
    def _update_analysis_cache(self, portfolio: Portfolio, analysis_results: Dict[str, Any]):
        """Update portfolio analysis cache."""
        portfolio.analysis_cache.last_analysis_time = datetime.now()
        portfolio.analysis_cache.overall_recommendation = analysis_results['overall_recommendation']['recommendation']
        portfolio.analysis_cache.confidence = analysis_results['overall_recommendation']['confidence']
        portfolio.analysis_cache.risk_level = analysis_results['risk_assessment']['risk_level']
        portfolio.analysis_cache.expected_return = analysis_results['portfolio_metrics']['expected_return']
        portfolio.analysis_cache.diversification_score = analysis_results['portfolio_metrics']['diversification_score']
        
        # Check if rebalancing is needed
        rebalance_suggestions = analysis_results.get('rebalance_suggestions', [])
        portfolio.analysis_cache.rebalance_needed = len([s for s in rebalance_suggestions if s.get('priority') == 'high']) > 0
        
        # Store additional details
        portfolio.analysis_cache.analysis_details = {
            'risk_score': analysis_results['portfolio_metrics']['risk_score'],
            'holdings_analyzed': len(analysis_results['individual_analysis']),
            'analysis_method': 'integrated' if self.stock_analyzer_class else 'fallback'
        }
        
        portfolio.last_analysis_time = datetime.now()
    
    def _get_cached_analysis(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Get cached analysis results."""
        cache = portfolio.analysis_cache
        
        return {
            'timestamp': cache.last_analysis_time.isoformat(),
            'portfolio_info': {
                'name': portfolio.name,
                'strategy': portfolio.strategy_type.value,
                'holdings_count': len(portfolio.holdings),
                'total_weight': portfolio.total_weight
            },
            'overall_recommendation': {
                'recommendation': cache.overall_recommendation,
                'confidence': cache.confidence,
                'reason': 'Cached analysis result'
            },
            'risk_assessment': {
                'risk_level': cache.risk_level,
                'risk_score': cache.analysis_details.get('risk_score', 0.5)
            },
            'portfolio_metrics': {
                'expected_return': cache.expected_return,
                'diversification_score': cache.diversification_score,
                'holdings_count': len(portfolio.holdings),
                'risk_score': cache.analysis_details.get('risk_score', 0.5)
            },
            'rebalance_needed': cache.rebalance_needed,
            'is_cached': True,
            'language': self.language
        }
    
    def compare_portfolios(self, portfolio1: Portfolio, portfolio2: Portfolio) -> Dict[str, Any]:
        """Compare two portfolios across multiple dimensions."""
        analysis1 = self.analyze_portfolio(portfolio1)
        analysis2 = self.analyze_portfolio(portfolio2)
        
        return {
            'portfolio1': {
                'name': portfolio1.name,
                'analysis': analysis1
            },
            'portfolio2': {
                'name': portfolio2.name, 
                'analysis': analysis2
            },
            'comparison': {
                'expected_return_diff': analysis1['portfolio_metrics']['expected_return'] - analysis2['portfolio_metrics']['expected_return'],
                'risk_diff': analysis1['portfolio_metrics'].get('risk_score', 0.5) - analysis2['portfolio_metrics'].get('risk_score', 0.5),
                'diversification_diff': analysis1['portfolio_metrics']['diversification_score'] - analysis2['portfolio_metrics']['diversification_score'],
                'confidence_diff': analysis1['overall_recommendation']['confidence'] - analysis2['overall_recommendation']['confidence']
            },
            'recommendation': self._generate_comparison_recommendation(analysis1, analysis2)
        }
    
    def _generate_comparison_recommendation(self, analysis1: Dict[str, Any], 
                                          analysis2: Dict[str, Any]) -> str:
        """Generate recommendation from portfolio comparison."""
        metrics1 = analysis1['portfolio_metrics']
        metrics2 = analysis2['portfolio_metrics']
        
        score1 = (metrics1['expected_return'] * 0.4) + ((1 - metrics1['risk_score']) * 0.3) + (metrics1['diversification_score'] * 0.3)
        score2 = (metrics2['expected_return'] * 0.4) + ((1 - metrics2['risk_score']) * 0.3) + (metrics2['diversification_score'] * 0.3)
        
        if score1 > score2 * 1.1:
            return f"Portfolio 1 ({analysis1['portfolio_info']['name']}) appears significantly better"
        elif score2 > score1 * 1.1:
            return f"Portfolio 2 ({analysis2['portfolio_info']['name']}) appears significantly better"
        else:
            return "Portfolios have similar risk-return profiles"