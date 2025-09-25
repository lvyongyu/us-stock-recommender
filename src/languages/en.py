"""
English language resources for US Stock Recommendation System
"""

# General UI text
TEXTS = {
    # General UI
    "analyzing": "Analyzing stock: {}...",
    "error": "Error: {}",
    
    # Data fetching errors
    "no_data_found": "Unable to fetch data for stock {}",
    "fetch_data_failed": "Data fetching failed: {}",
    "data_required": "Please fetch stock data first",
    
    # Report Header
    "report_title": "US STOCK INVESTMENT STRATEGY REPORT",
    "stock_code": "Stock Symbol",
    "current_price": "Current Price",
    "price_change": "Price Change",
    "analysis_time": "Analysis Time",
    
    # Technical Analysis
    "technical_analysis": "TECHNICAL ANALYSIS",
    "trend_analysis": "Trend Analysis",
    "momentum_indicators": "Momentum Indicators",
    "volume_analysis": "Volume Analysis",
    "key_metrics": "Key Technical Indicators",
    
    # Investment Recommendation
    "investment_advice": "INVESTMENT RECOMMENDATION",
    "recommended_action": "Recommended Action",
    "confidence_level": "Confidence Level",
    "risk_rating": "Risk Rating",
    "composite_score": "Composite Score",
    "analysis_basis": "Analysis Basis",
    
    # Actions
    "strong_buy": "Strong Buy",
    "buy": "Buy",
    "hold": "Hold",
    "sell": "Sell",
    "strong_sell": "Strong Sell/Short",
    
    # Confidence Levels
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    
    # Risk Levels
    "low_risk": "Low Risk",
    "medium_risk": "Medium Risk",
    "high_risk": "High Risk",
    
    # Trends
    "uptrend": "Uptrend",
    "downtrend": "Downtrend",
    "sideways": "Sideways",
    
    # Momentum
    "rsi_neutral": "RSI Neutral",
    "rsi_overbought": "RSI Overbought",
    "rsi_oversold": "RSI Oversold",
    "macd_bullish": "MACD Bullish",
    "macd_bearish": "MACD Bearish",
    
    # Volume
    "volume_normal": "Normal Volume",
    "volume_high": "High Volume",
    "volume_low": "Low Volume",
    
    # Technical Analysis Signals
    "price_above_sma20": "Price above 20-day SMA",
    "price_below_sma20": "Price below 20-day SMA",
    "sma_golden_cross": "Short-term SMA crosses above long-term SMA",
    "sma_death_cross": "Short-term SMA crosses below long-term SMA",
    "macd_golden_cross": "MACD golden cross bullish",
    "macd_death_cross": "MACD death cross bearish",
    "rsi_overbought_signal": "RSI overbought, potential pullback",
    "rsi_oversold_signal": "RSI oversold, potential bounce",
    "rsi_neutral_zone": "RSI in neutral zone",
    "bollinger_upper": "Price touches Bollinger upper band",
    "bollinger_lower": "Price touches Bollinger lower band",
    
    # Disclaimer
    "disclaimer": "Disclaimer: This analysis is for reference only. Stock investment involves risks, please invest cautiously!",
    
    # Command line help
    "help_symbol": "Stock symbol (e.g., AAPL, TSLA, MSFT)",
    "help_period": "Data time period (default: 1y)",
    "help_language": "Language: en (English) or zh (Chinese) (default: en)",
    "help_description": "US Stock Recommendation System / 美股推荐系统",
    "help_strategy": "Trading strategy: technical, quantitative, ai, or all (default: all)",
    "help_single_stock_mode": "(Single stock mode)",
    "help_multi_stock_mode": "Multi-stock mode: optionally provide comma-separated stock symbols (<5), or use with --file",
    "help_file_input": "Stock list file path (used with --multi)",
    
    # Strategy Names
    "strategy_technical": "Technical Indicators",
    "strategy_quantitative": "Quantitative Model", 
    "strategy_ai": "AI/Machine Learning",
    "strategy_combined": "Combined Strategies",
    
    # Technical Strategy Reasons
    "strategy_rsi_oversold": "RSI({:.1f}) is oversold, potential buying opportunity",
    "strategy_rsi_overbought": "RSI({:.1f}) is overbought, potential selling pressure", 
    "strategy_rsi_neutral": "RSI({:.1f}) is in neutral zone, moderate signal",
    "strategy_macd_strong_bullish": "MACD above signal line and zero, strong bullish trend",
    "strategy_macd_bullish": "MACD above signal line, bullish momentum",
    "strategy_macd_strong_bearish": "MACD below signal line and zero, strong bearish trend",
    "strategy_macd_bearish": "MACD below signal line, bearish momentum",
    "strategy_ma_strong_uptrend": "Price above both short and long moving averages, strong uptrend",
    "strategy_ma_above_short": "Price above short-term moving average, positive momentum",
    "strategy_ma_strong_downtrend": "Price below both moving averages, strong downtrend", 
    "strategy_ma_below_short": "Price below short-term moving average, negative momentum",
    "strategy_bb_oversold": "Price below Bollinger lower band, potentially oversold",
    "strategy_bb_overbought": "Price above Bollinger upper band, potentially overbought",
    "strategy_bb_above_middle": "Price above Bollinger middle band, bullish bias",
    
    # Quantitative Strategy Reasons
    "strategy_momentum_strong": "Strong momentum: {:.1f}% (5D), {:.1f}% (20D), bullish trend",
    "strategy_momentum_positive": "Positive momentum: {:.1f}% (5D), {:.1f}% (20D), upward bias",
    "strategy_momentum_weak": "Weak momentum: {:.1f}% (5D), {:.1f}% (20D), bearish trend", 
    "strategy_momentum_negative": "Negative momentum: {:.1f}% (5D), {:.1f}% (20D), downward bias",
    "strategy_volatility_low": "Low volatility environment, favorable for trend continuation",
    "strategy_volatility_high": "High volatility environment, increased risk",
    "strategy_volume_surge_bullish": "Volume surge ({:.1f}x average) with positive price action",
    "strategy_volume_surge_bearish": "Volume surge ({:.1f}x average) with negative price action",
    "strategy_volume_low": "Below average volume, lack of conviction",
    "strategy_mean_reversion_oversold": "Price {:.1f}% below mean, potential mean reversion opportunity", 
    "strategy_mean_reversion_overbought": "Price {:.1f}% above mean, potential mean reversion risk",
    "strategy_mean_reversion_fair": "Price near fair value based on mean reversion model",
    
    # AI/ML Strategy Reasons  
    "strategy_ml_rsi_oversold": "ML model detects RSI oversold condition",
    "strategy_ml_rsi_overbought": "ML model detects RSI overbought condition",
    "strategy_ml_macd_bullish": "ML model identifies bullish MACD pattern",
    "strategy_ml_macd_bearish": "ML model identifies bearish MACD pattern", 
    "strategy_ml_bullish_prediction": "AI prediction: {:.0f}% confidence bullish trend",
    "strategy_ml_bearish_prediction": "AI prediction: {:.0f}% confidence bearish trend",
    "strategy_ml_neutral_prediction": "AI prediction shows neutral/sideways trend",
    "strategy_ml_fallback": "ML analysis unavailable, using technical fallback",
    
    # Combined Strategy
    "strategy_consensus_strong": "Strong consensus across multiple strategies",
    "strategy_consensus_moderate": "Moderate consensus across strategies", 
    "strategy_consensus_mixed": "Mixed signals from different strategies",
    "strategy_weight_technical": "Technical analysis weight: {}%",
    "strategy_weight_quantitative": "Quantitative model weight: {}%", 
    "strategy_weight_ai": "AI/ML model weight: {}%",
    
    # Batch Analysis
    "batch_analysis_start": "🚀 Starting batch stock analysis...",
    "batch_stock_count": "📊 Number of stocks: {}",
    "batch_strategy": "📈 Analysis strategy: {}",
    "batch_period": "📅 Data period: {}",
    "batch_concurrent_config": "⚙️  Concurrent config: {} threads, {}s interval",
    "batch_analysis_complete": "📈 Batch analysis completed",
    "batch_total_stocks": "📊 Total stocks: {}",
    "batch_success_rate": "✅ Success: {} ({:.1f}%)",
    "batch_failed_count": "❌ Failed: {}",
    "batch_total_time": "⏱️  Total time: {}",
    "batch_failed_details": "❌ Failed task details:",
    "batch_avg_time": "📈 Average processing time: {}",
    "batch_analysis_summary": "📈 Multi-stock analysis summary",
    
    # Error Messages - Friendly
    "error_stock_not_exist_suggest": "{}: Stock code does not exist, you might want to enter {}",
    "error_acquired_by": "{}: {}",
    "error_bank_closed": "{}: {}",
    "error_stock_delisted": "{}: Stock may be delisted or code is invalid",
    "error_network_issue": "{}: Network connection issue, please try again later",
    
    # Progress Tracking
    "progress_calculating": "Calculating...",
    "progress_estimated_remaining": "Estimated remaining: {}",
    
    # Investment Portfolio
    "portfolio_title": "💼 Investment Portfolio Recommendations:",
    "portfolio_top_picks": "🎯 Top picks (top {}): {}",
    "buy_recommendations": "🟢 Buy Recommendations ({} stocks):",
    "hold_recommendations": "⚪ Hold Recommendations ({} stocks):",
    "sell_recommendations": "🔴 Sell/Short Recommendations ({} stocks):",
    "stock_score_confidence": "{} - Score: {}, Confidence: {}",
    
    # Multi-stock UI Messages
    "stock_recommendation_results": "📈 Stock Recommendation Results",
    "no_successful_analysis": "❌ No successful analysis results",
    "short_recommendations": "🟡 Short Recommendations ({} stocks):",
    "risk_stocks": "⚠️  High-risk stocks: {}",
    "no_valid_stock_input": "❌ No valid stock input provided",
    "input_parsing_warnings": "⚠️  Input parsing warnings:",
    "no_valid_stock_symbols": "❌ No valid stock symbols found",
    "parsing_summary": "📊 Successfully parsed {}/{} stocks",
    "multi_stock_analysis_failed": "❌ Multi-stock analysis failed: {}",
    "error_must_specify_stock": "Error: Must specify stock symbol or use multi-stock mode",
    
    # Input Parser Error Messages
    "cannot_use_both_input": "Cannot use both command line and file input simultaneously",
    "must_specify_input": "Must specify stock symbols or file path",
    "command_line_limit_exceeded": "Command line input exceeds {} stocks, please use file input",
    "file_not_found": "File does not exist: {}",
    "unsupported_file_format": "Unsupported file format: {}",
    "parsing_failed": "Input parsing failed: {}",
    "file_parsing_failed": "Failed to parse file: {}",
    "concurrent_manager_context_required": "ConcurrentManager must be used within a 'with' statement",
    "task_execution_exception": "Task execution exception: {}"
}
