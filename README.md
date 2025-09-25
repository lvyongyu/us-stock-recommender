# US Stock Recommendation System - Intelligent Investment Strategy System Based on Technical Analysis

A powerful multi-language US stock analysis and recommendation system with modular architecture design, supporting multiple analysis strategies and comprehensive testing framework.

## 📖 Documentation

- [🇺🇸 English](README.md) ← You are here
- [🇨🇳 中文文档](README.zh.md)

## Features

- 🌐 **Multi-language Support**: Support English and Chinese interface switching with complete internationalization architecture
- 📈 **Real-time Stock Data**: Uses yfinance library to fetch real-time stock data from Yahoo Finance
- 🔍 **Multiple Analysis Strategies**: 
  - Technical Analysis Strategy
  - Quantitative Analysis Strategy  
  - AI/ML Strategy
  - Combined Strategy
- 🎯 **Smart Recommendation Engine**: Automatically generates investment recommendations based on multiple indicators
- 📊 **Risk Assessment System**: Automatic investment risk level and confidence assessment
- 📋 **Detailed Reports**: Generate comprehensive bilingual analysis reports
- 🧪 **Comprehensive Testing**: Full coverage with unit tests, integration tests, and performance tests

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install us-stock-recommender
```

After installation, you can use the command directly:
```bash
stock-recommender AAPL
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/lvyongyu/us-stock-recommender.git
cd us-stock-recommender

# Install dependencies
pip3 install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# English Version (Default)
python3 stock_recommender.py AAPL

# Chinese Version
python3 stock_recommender.py AAPL --lang zh

# Specify Analysis Strategy
python3 stock_recommender.py AAPL --strategy technical --lang en
python3 stock_recommender.py AAPL --strategy quantitative --lang zh
```

### Specify Data Time Range

```bash
# English Version
python3 stock_recommender.py TSLA --period 6mo --lang en

# Chinese Version
python3 stock_recommender.py TSLA --period 6mo --lang zh
```

### Supported Analysis Strategies
- `technical`: Technical Analysis Strategy
- `quantitative`: Quantitative Analysis Strategy
- `ai`: AI/Machine Learning Strategy
- `combined`: Combined Strategy (Default)

### Supported Time Periods
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

### Supported Languages
- `en`: English
- `zh`: Chinese

### Batch Analysis Mode 🆕

The system supports multi-stock batch analysis functionality, enabling simultaneous analysis of multiple stocks with comprehensive reporting.

#### Command Line Batch Analysis (Up to 5 stocks)

```bash
# English batch analysis
python3 stock_recommender.py --multi "AAPL,MSFT,GOOGL,TSLA" --lang en

# Chinese batch analysis
python3 stock_recommender.py --multi "AAPL,MSFT,GOOGL,TSLA" --lang zh

# Strategy-specific batch analysis
python3 stock_recommender.py --multi "AAPL,MSFT,GOOGL" --strategy technical --lang en
```

#### File-based Batch Analysis (Support for large stock lists)

```bash
# Batch analysis from TXT file
python3 stock_recommender.py --multi --file stocks.txt --lang en

# Batch analysis from CSV file  
python3 stock_recommender.py --multi --file stocks.csv --lang zh
```

#### Supported File Formats

**TXT Format Example** (`stocks.txt`):
```
# Stock list
AAPL
MSFT
GOOGL
TSLA

# Comma-separated format also supported
NVDA, AMD, INTC
```

**CSV Format Example** (`stocks.csv`):
```csv
Symbol,Company,Sector
AAPL,Apple Inc,Technology
MSFT,Microsoft Corporation,Technology
GOOGL,Alphabet Inc,Technology
TSLA,Tesla Inc,Consumer Discretionary
```

#### Batch Analysis Features

- 📊 **Concurrent Processing**: Smart concurrent management for improved analysis efficiency
- 📈 **Real-time Progress**: Live progress bar showing analysis status
- 🎯 **Smart Retry**: Automatic retry for failed stock analyses
- 📋 **Categorized Summary**: Auto-categorization of results by investment recommendations
- 🛡️ **Error Handling**: User-friendly error messages and stock symbol correction
- ⚡ **Speed Optimization**: API rate limiting and resource management

#### Batch Analysis Output Example

```
================================================================================
                          US STOCK INVESTMENT RECOMMENDATIONS
================================================================================

📈 Strong Buy Recommendations (2 stocks):
   • AAPL: Strong Buy (Score: 75) - Strong technical indicators, clear uptrend
   • MSFT: Strong Buy (Score: 68) - Excellent fundamentals, good momentum

💼 Buy Recommendations (1 stock):
   • GOOGL: Buy (Score: 45) - Positive technical indicators, upside potential

⚖️ Hold Recommendations (1 stock):  
   • TSLA: Hold (Score: 5) - Sideways consolidation, awaiting breakout

📊 Batch Analysis Summary:
   Total Stocks: 4
   Successfully Analyzed: 4 (100.0%)
   Failed: 0
   Analysis Time: 12.3s
```

## Analysis Indicators

### Technical Indicators
- **Moving Averages**: SMA20, SMA50
- **Exponential Moving Averages**: EMA12, EMA26
- **MACD**: Trend Following Indicator
- **RSI**: Relative Strength Index (Overbought/Oversold Indicator)
- **Bollinger Bands**: Price Volatility Range
- **Volume Analysis**: Volume Anomaly Detection

### Recommendation Strategies
- **Strong Buy**: Composite Score >= 50
- **Buy**: Composite Score >= 25
- **Hold**: Composite Score -25 to 25
- **Sell**: Composite Score -50 to -25
- **Strong Sell/Short**: Composite Score <= -50

## 📚 Documentation

For detailed analysis of the strategy system and implementation:

- **[Strategy Analysis (中文)](./docs/STRATEGY_ANALYSIS.md)** - Complete strategy system analysis and implementation details
- **[Strategy Analysis (English)](./docs/STRATEGY_ANALYSIS_EN.md)** - English version of strategy analysis
- **[Quick Reference (快速参考)](./docs/STRATEGY_QUICK_REFERENCE.md)** - Quick reference guide for strategy usage
- **[Documentation Index](./docs/README.md)** - Complete documentation directory

## Example Output

### English Version

```
============================================================
           US STOCK INVESTMENT STRATEGY REPORT
============================================================

Stock Symbol: AAPL
Current Price: $254.43
Price Change: $-1.65 (-0.64%)
Analysis Time: 2025-09-24 22:39:20

============================================================
TECHNICAL ANALYSIS
============================================================
Trend Analysis: Uptrend
Momentum Indicators: RSI Neutral | MACD Bullish
Volume Analysis: Normal Volume

Key Technical Indicators:
- RSI: 66.81
- MACD: 6.3762
- SMA 20: $237.15
- SMA 50: $225.65

============================================================
INVESTMENT RECOMMENDATION
============================================================
Recommended Action: Strong Buy
Confidence Level: High
Risk Rating: Low Risk
Composite Score: 50/100

Analysis Basis:
1. Price above 20-day SMA
2. Short-term SMA crosses above long-term SMA
3. MACD golden cross bullish
4. Price touches Bollinger upper band
```

## Project Structure

```
stock recommander/
├── stock_recommender.py          # Main program entry
├── requirements.txt              # Dependencies list
├── setup.cfg                     # Project configuration
├── pyproject.toml                # Project configuration and packaging info
├── run_ci_tests.sh              # CI test script
├── README.md                    # Project documentation (English)
├── README.zh.md                 # Chinese documentation
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore file
├── src/                         # Source code directory
│   ├── __init__.py             # Package initialization
│   ├── analyzers/              # Stock analyzer modules
│   │   ├── __init__.py
│   │   └── stock_analyzer.py   # Core stock data analysis
│   ├── engines/                # Recommendation engine modules
│   │   ├── __init__.py
│   │   ├── recommendation_engine.py  # Recommendation engine
│   │   └── strategy_manager.py      # Strategy manager
│   ├── strategies/             # Analysis strategy modules
│   │   ├── __init__.py
│   │   ├── base_strategy.py    # Base strategy class
│   │   ├── technical_strategy.py   # Technical analysis strategy
│   │   ├── quantitative_strategy.py # Quantitative analysis strategy
│   │   └── aiml_strategy.py    # AI/ML analysis strategy
│   ├── batch/                  # Batch analysis modules 🆕
│   │   ├── __init__.py
│   │   ├── input_parser.py     # Multi-format input parser
│   │   ├── batch_analyzer.py   # Batch stock analyzer
│   │   ├── concurrent_manager.py # Concurrent processing manager
│   │   ├── progress_tracker.py # Real-time progress tracker
│   │   ├── sample_stocks.txt   # Sample stock list file
│   │   └── sample_stocks.csv   # Sample stock CSV file
│   ├── languages/              # Multi-language support modules
│   │   ├── __init__.py
│   │   ├── config.py          # Language configuration management
│   │   ├── en.py             # English text resources
│   │   └── zh.py             # Chinese text resources
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       ├── formatters.py      # Formatting utilities
│       └── symbol_config.py   # Stock symbol configuration and correction
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── run_tests.py           # Test runner
│   ├── test_stock_analyzer.py  # Stock analyzer tests
│   ├── test_strategies.py     # Strategy tests
│   ├── test_engines.py        # Engine tests
│   ├── test_integration.py    # Integration tests
│   ├── test_language_config.py # Language config tests
│   ├── test_input_parser.py   # Input parser tests 🆕
│   ├── test_multi_stock_integration.py # Multi-stock integration tests 🆕
│   └── test_utils.py          # Test configuration and mock data
├── docs/                       # Documentation directory
│   ├── README.md              # Documentation index
│   ├── STRATEGY_ANALYSIS.md   # Strategy analysis documentation (Chinese)
│   ├── STRATEGY_ANALYSIS_EN.md # Strategy analysis documentation (English)
│   ├── PYPI_PUBLISHING_GUIDE.md # PyPI publishing guide
│   └── RELEASE_CHECKLIST.md   # Release checklist
├── scripts/                    # Scripts directory
│   └── prepare_release.sh     # Release preparation script
├── .github/                    # GitHub configuration
│   ├── workflows/             # GitHub Actions workflows
│   └── copilot-instructions.md # Copilot instructions configuration
├── test_stocks.txt            # Test stock list
├── test_500_stocks.txt        # Large stock list for testing
├── test_error_handling.txt    # Error handling test list
└── test_alpha_vantage.py      # Alpha Vantage API test script
```

## Core Architecture Design

### Modular Layered Architecture

1. **Presentation Layer**: `stock_recommender.py`
   - Command-line interface and user interaction
   - Parameter parsing and output formatting

2. **Business Logic Layer**: `src/engines/`
   - Recommendation engine coordinates various strategies
   - Strategy management and result aggregation

3. **Analysis Strategy Layer**: `src/strategies/`
   - Pluggable analysis strategy implementations
   - Technical, quantitative, AI/ML analysis

4. **Data Access Layer**: `src/analyzers/`
   - Stock data fetching and preprocessing
   - Technical indicator calculations

5. **Infrastructure Layer**: `src/languages/`, `src/utils/`
   - Multi-language support and utility functions

### Multi-language Internationalization Architecture

The project uses a complete internationalization architecture design:

- **`src/languages/config.py`**: Language configuration management core
- **`src/languages/en.py`**: English resource file
- **`src/languages/zh.py`**: Chinese resource file
- **`LanguageConfig` class**: Dynamic language switching and resource loading

**Architecture Advantages:**
- ✅ **Complete Decoupling**: Code logic separated from text resources
- ✅ **Type Safety**: All text keys have type checking
- ✅ **Easy Extension**: Add new languages by adding resource files
- ✅ **Runtime Switching**: Support runtime language switching

## Testing Framework

The project includes a comprehensive testing system:

```bash
# Run complete CI test suite
bash run_ci_tests.sh

# Run specific test modules  
python3 -m pytest tests/test_strategies.py
python3 -m pytest tests/test_integration.py
```

**Test Coverage:**
- 📋 **Unit Tests**: Independent functionality tests for each module
- 🔗 **Integration Tests**: Inter-module collaboration and end-to-end tests
- 🚀 **Performance Tests**: System response time and resource usage tests
- 🧪 **Smoke Tests**: Quick verification of core functionality
- 🌐 **Multi-language Tests**: Internationalization functionality integrity tests

## Development and Deployment

### Development Environment Setup

```bash
# Clone project
git clone https://github.com/lvyongyu/us-stock-recommender.git
cd "stock recommander"

# Install dependencies
pip3 install -r requirements.txt

# Run tests
bash run_ci_tests.sh

# Run program
python3 stock_recommender.py AAPL --lang en
```

### Recommended Development Environment

- **Python**: 3.8+ (Recommended 3.9+)
- **IDE**: VS Code, PyCharm, or other Python-supported IDE
- **Git**: Latest version
- **OS**: macOS, Linux, Windows (Unix-like systems recommended)

## Tech Stack

### Core Dependencies
- **Python 3.8+**: Main programming language
- **yfinance**: Stock data fetching
- **pandas**: Data processing and analysis  
- **numpy**: Numerical computation and technical indicators

### Development Tools
- **unittest**: Unit testing framework
- **argparse**: Command-line argument parsing
- **datetime**: Time and date processing

### Optional Extensions
- **matplotlib & seaborn**: Data visualization
- **scikit-learn**: Machine learning algorithms
- **ta-lib**: Advanced technical analysis library

## Disclaimer

⚠️ **Important Notice**: This software is for educational and reference purposes only and does not constitute investment advice. Stock market involves risks, please invest cautiously! The risks of making investment decisions using this software are borne by the user.

## Future Enhancement Plans

### Short-term Plans
- [ ] 📈 Add chart visualization features
- [ ] 🔔 Real-time price monitoring and alerts
- [ ] 📊 Add more technical indicators
- [ ] 🧠 Improve AI/ML strategy algorithms

### Medium-term Plans
- [ ] 🎯 Support multi-stock portfolio analysis
- [ ] 📰 Integrate news sentiment analysis
- [ ] 🔄 Add backtesting functionality
- [ ] 🌐 Create web interface

### Long-term Plans
- [ ] 📱 Mobile app development
- [ ] 🤖 Advanced AI prediction models
- [ ] ☁️ Cloud deployment and API services
- [ ] 🔗 Integrate more data sources

## Contributing Guidelines

### How to Contribute
1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Standards
- Follow PEP 8 Python coding standards
- All new features must include tests
- Maintain test coverage above 90%
- Update relevant documentation
- Ensure CI tests pass

Welcome to submit Issues and Pull Requests to improve this project!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
