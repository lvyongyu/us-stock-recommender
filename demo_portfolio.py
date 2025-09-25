#!/usr/bin/env python3
"""
Portfolio Management System Demonstration

Demonstrates the complete portfolio management functionality including:
- Portfolio creation and management
- Stock position tracking
- Portfolio-level analysis and recommendations
- Risk assessment and diversification analysis
- Comparison between portfolios

Usage:
    python demo_portfolio.py
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.portfolio import PortfolioManager, PortfolioAnalyzer, StrategyType


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_portfolio_info(portfolio):
    """Print detailed portfolio information."""
    print(f"\n📊 Portfolio: {portfolio.name}")
    print(f"   Strategy: {portfolio.strategy_type.value}")
    print(f"   Description: {portfolio.description}")
    print(f"   Holdings: {len(portfolio.holdings)}")
    print(f"   Total Weight: {portfolio.total_weight:.1%}")
    
    if portfolio.holdings:
        print(f"\n   📈 Holdings:")
        for holding in portfolio.holdings:
            target_info = f" → {holding.target_weight:.1%}" if holding.target_weight else ""
            deviation_info = ""
            if holding.target_weight:
                deviation = holding.get_weight_deviation()
                if deviation:
                    deviation_info = f" ({deviation:+.1%})"
            
            print(f"     {holding.symbol}: {holding.weight:.1%}{target_info}{deviation_info}")
            if holding.notes:
                print(f"       Notes: {holding.notes}")


def print_analysis_summary(analysis_results):
    """Print portfolio analysis summary."""
    print(f"\n🔍 Analysis Summary:")
    
    overall = analysis_results['overall_recommendation']
    metrics = analysis_results['portfolio_metrics']
    risk = analysis_results['risk_assessment']
    
    print(f"   Recommendation: {overall['strength']} ({overall['confidence']:.0%} confidence)")
    print(f"   Expected Return: {metrics['expected_return']:.1%}")
    print(f"   Risk Level: {risk['risk_level']} (Score: {risk['risk_score']:.2f})")
    print(f"   Diversification: {metrics['diversification_score']:.0%}")
    print(f"   Reason: {overall['reason']}")
    
    if risk['risk_factors']:
        print(f"   Risk Factors: {', '.join(risk['risk_factors'])}")
    
    rebalance_suggestions = analysis_results.get('rebalance_suggestions', [])
    if rebalance_suggestions:
        print(f"   Rebalancing: {len(rebalance_suggestions)} suggestions available")


def demo_portfolio_creation():
    """Demonstrate portfolio creation and management."""
    print_header("Portfolio Creation and Management")
    
    manager = PortfolioManager()
    
    # Clean up any existing demo portfolios first
    print("🧹 Cleaning up any existing demo portfolios...")
    existing_demos = []
    for portfolio in manager.list_portfolios():
        if "Demo" in portfolio.name:
            existing_demos.append(portfolio.name)
    
    for demo_name in existing_demos:
        try:
            manager.delete_portfolio(demo_name)
            print(f"   Removed existing: {demo_name}")
        except:
            pass
    
    # Create different types of portfolios
    print("📝 Creating sample portfolios...")
    
    # Tech-focused aggressive portfolio
    tech_portfolio = manager.create_portfolio(
        "Demo Tech Growth", 
        description="Technology-focused growth portfolio",
        strategy_type=StrategyType.AGGRESSIVE
    )
    
    manager.add_stock("Demo Tech Growth", "AAPL", 0.30, target_weight=0.25, notes="iPhone growth story")
    manager.add_stock("Demo Tech Growth", "MSFT", 0.25, target_weight=0.25, notes="Cloud computing leader")
    manager.add_stock("Demo Tech Growth", "GOOGL", 0.25, target_weight=0.25, notes="AI and search dominance")
    manager.add_stock("Demo Tech Growth", "TSLA", 0.20, target_weight=0.25, notes="EV market leader")
    
    # Balanced conservative portfolio
    balanced_portfolio = manager.create_portfolio(
        "Demo Balanced", 
        description="Balanced portfolio with diversified holdings",
        strategy_type=StrategyType.CONSERVATIVE
    )
    
    manager.add_stock("Demo Balanced", "VTI", 0.40, target_weight=0.35, notes="US total market")
    manager.add_stock("Demo Balanced", "BND", 0.25, target_weight=0.30, notes="Bond exposure")
    manager.add_stock("Demo Balanced", "VEA", 0.20, target_weight=0.20, notes="International developed")
    manager.add_stock("Demo Balanced", "VWO", 0.15, target_weight=0.15, notes="Emerging markets")
    
    print("✅ Sample portfolios created successfully!")
    
    return manager, tech_portfolio, balanced_portfolio


def demo_portfolio_analysis():
    """Demonstrate portfolio analysis functionality."""
    print_header("Portfolio Analysis")
    
    manager, tech_portfolio, balanced_portfolio = demo_portfolio_creation()
    analyzer = PortfolioAnalyzer(language='en')
    
    # Analyze each portfolio
    for portfolio in [tech_portfolio, balanced_portfolio]:
        print_portfolio_info(portfolio)
        
        print(f"\n🔍 Analyzing {portfolio.name}...")
        analysis = analyzer.analyze_portfolio(portfolio)
        print_analysis_summary(analysis)
        
        # Show individual stock analysis
        individual = analysis['individual_analysis']
        print(f"\n   📈 Individual Stock Analysis:")
        for symbol, stock_analysis in individual.items():
            print(f"     {symbol}: {stock_analysis['recommendation']} "
                  f"({stock_analysis['confidence']:.0%} confidence, "
                  f"Risk: {stock_analysis['risk_score']:.2f})")
    
    return manager, analyzer, tech_portfolio, balanced_portfolio


def demo_portfolio_comparison():
    """Demonstrate portfolio comparison functionality."""
    print_header("Portfolio Comparison")
    
    manager, analyzer, tech_portfolio, balanced_portfolio = demo_portfolio_analysis()
    
    print(f"🔄 Comparing portfolios...")
    comparison = analyzer.compare_portfolios(tech_portfolio, balanced_portfolio)
    
    print(f"\n📊 Comparison Results:")
    print(f"   Portfolio 1: {comparison['portfolio1']['name']}")
    print(f"   Portfolio 2: {comparison['portfolio2']['name']}")
    
    comp_metrics = comparison['comparison']
    print(f"\n   📈 Performance Differences:")
    print(f"     Expected Return: {comp_metrics['expected_return_diff']:+.1%}")
    print(f"     Risk Score: {comp_metrics['risk_diff']:+.2f}")
    print(f"     Diversification: {comp_metrics['diversification_diff']:+.1%}")
    print(f"     Confidence: {comp_metrics['confidence_diff']:+.1%}")
    
    print(f"\n   💡 Recommendation: {comparison['recommendation']}")
    
    return manager, analyzer


def demo_rebalancing():
    """Demonstrate portfolio rebalancing functionality."""
    print_header("Portfolio Rebalancing")
    
    manager, analyzer = demo_portfolio_comparison()
    
    # Get a portfolio that needs rebalancing
    portfolios = manager.list_portfolios()
    demo_portfolio = None
    
    for portfolio in portfolios:
        if "Demo Tech Growth" in portfolio.name:
            demo_portfolio = portfolio
            break
    
    if demo_portfolio:
        print_portfolio_info(demo_portfolio)
        
        print(f"\n⚖️ Current weights vs targets:")
        for holding in demo_portfolio.holdings:
            if holding.target_weight:
                deviation = holding.get_weight_deviation()
                status = "❌ Needs rebalancing" if abs(deviation or 0) > 0.02 else "✅ On target"
                print(f"   {holding.symbol}: {holding.weight:.1%} → {holding.target_weight:.1%} "
                      f"({deviation:+.1%}) {status}")
        
        # Perform rebalancing
        print(f"\n🔄 Rebalancing portfolio to target weights...")
        manager.rebalance_to_targets(demo_portfolio.name)
        
        print(f"✅ Portfolio rebalanced!")
        print_portfolio_info(demo_portfolio)
    
    return manager


def demo_batch_operations():
    """Demonstrate batch operations."""
    print_header("Batch Operations")
    
    manager = demo_rebalancing()
    
    # Demonstrate batch stock addition
    print("📦 Adding multiple stocks to portfolio...")
    
    batch_stocks = [
        ("NVDA", 0.10, 0.12, "GPU and AI leader"),
        ("AMD", 0.08, 0.08, "CPU competition"),
        ("INTC", 0.07, 0.05, "Semiconductor recovery play")
    ]
    
    demo_portfolio_name = None
    for portfolio in manager.list_portfolios():
        if "Demo Tech Growth" in portfolio.name:
            demo_portfolio_name = portfolio.name
            break
    
    if demo_portfolio_name:
        for symbol, weight, target, notes in batch_stocks:
            manager.add_stock(demo_portfolio_name, symbol, weight, target_weight=target, notes=notes)
        
        portfolio = manager.get_portfolio(demo_portfolio_name)
        print_portfolio_info(portfolio)
        
        # Show validation
        is_valid, total = portfolio.validate_weights()
        print(f"\n✅ Validation: {'Valid' if is_valid else 'Invalid'} (Total: {total:.1%})")
    
    return manager


def demo_persistence():
    """Demonstrate file persistence functionality."""
    print_header("File Persistence")
    
    manager = demo_batch_operations()
    
    print("💾 Saving portfolios to disk...")
    saved_portfolios = []
    
    for portfolio in manager.list_portfolios():
        if "Demo" in portfolio.name:
            manager.save_portfolio(portfolio.name)
            saved_portfolios.append(portfolio.name)
    
    print(f"✅ Saved {len(saved_portfolios)} portfolios")
    
    # Show file locations
    print(f"\n📁 Portfolio files:")
    for portfolio_name in saved_portfolios:
        filename = manager._get_portfolio_filename(portfolio_name)
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   {portfolio_name}: {filename} ({size} bytes)")
    
    print(f"\n🔄 Testing portfolio reload...")
    
    # Clear memory and reload
    original_count = len(manager.portfolios)
    manager.portfolios.clear()
    print(f"   Cleared {original_count} portfolios from memory")
    
    # Reload
    manager.load_all_portfolios()
    print(f"   Reloaded {len(manager.portfolios)} portfolios from disk")
    
    return manager


def demo_error_handling():
    """Demonstrate error handling."""
    print_header("Error Handling")
    
    manager = demo_persistence()
    
    test_cases = [
        ("Creating duplicate portfolio", lambda: manager.create_portfolio("Demo Tech Growth", strategy_type=StrategyType.BALANCED)),
        ("Adding stock to non-existent portfolio", lambda: manager.add_stock("NonExistent", "AAPL", 0.5)),
        ("Adding duplicate stock", lambda: manager.add_stock("Demo Tech Growth", "AAPL", 0.1)),
        ("Invalid weight (negative)", lambda: manager.add_stock("Demo Tech Growth", "TEST", -0.1)),
        ("Invalid weight (too large)", lambda: manager.add_stock("Demo Tech Growth", "TEST", 1.5)),
    ]
    
    for description, test_func in test_cases:
        try:
            test_func()
            print(f"   ❌ {description}: Expected error but none occurred")
        except Exception as e:
            error_type = type(e).__name__
            print(f"   ✅ {description}: {error_type} - {str(e)[:50]}...")


def demo_multilanguage():
    """Demonstrate multi-language support."""
    print_header("Multi-language Support")
    
    manager = demo_persistence()
    
    # Get a portfolio for analysis
    portfolio = None
    for p in manager.list_portfolios():
        if "Demo Balanced" in p.name:
            portfolio = p
            break
    
    if portfolio:
        print(f"📊 Analyzing portfolio in different languages...")
        
        # English analysis
        en_analyzer = PortfolioAnalyzer(language='en')
        en_analysis = en_analyzer.analyze_portfolio(portfolio)
        
        print(f"\n🇺🇸 English Analysis:")
        print(f"   Risk Level: {en_analysis['risk_assessment']['risk_level']}")
        print(f"   Recommendation: {en_analysis['overall_recommendation']['recommendation']}")
        
        # Chinese analysis
        zh_analyzer = PortfolioAnalyzer(language='zh')
        zh_analysis = zh_analyzer.analyze_portfolio(portfolio)
        
        print(f"\n🇨🇳 中文分析:")
        print(f"   风险等级: {zh_analysis['risk_assessment']['risk_level']}")
        print(f"   推荐: {zh_analysis['overall_recommendation']['recommendation']}")


def cleanup_demo_portfolios():
    """Clean up demo portfolios."""
    print_header("Cleanup")
    
    manager = PortfolioManager()
    
    demo_portfolios = []
    for portfolio in manager.list_portfolios():
        if "Demo" in portfolio.name:
            demo_portfolios.append(portfolio.name)
    
    print(f"🗑️  Cleaning up {len(demo_portfolios)} demo portfolios...")
    
    for portfolio_name in demo_portfolios:
        try:
            manager.delete_portfolio(portfolio_name)
            print(f"   ✅ Deleted: {portfolio_name}")
        except Exception as e:
            print(f"   ❌ Failed to delete {portfolio_name}: {e}")


def main():
    """Run the complete portfolio management system demonstration."""
    print("🎯 Portfolio Management System Demo")
    print("This demonstration shows the complete functionality of the portfolio management system.")
    
    try:
        # Run all demonstrations
        demo_portfolio_creation()
        demo_portfolio_analysis()
        demo_portfolio_comparison()
        demo_rebalancing()
        demo_batch_operations()
        demo_persistence()
        demo_error_handling()
        demo_multilanguage()
        
        print_header("Demo Complete!")
        print("✅ All portfolio management features demonstrated successfully!")
        
        # Ask if user wants to cleanup
        response = input("\nDelete demo portfolios? (y/N): ").strip().lower()
        if response == 'y':
            cleanup_demo_portfolios()
        else:
            print("Demo portfolios preserved for further exploration.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Thank you for exploring the Portfolio Management System!")


if __name__ == "__main__":
    main()