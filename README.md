# 美股推荐软件 (US Stock Recommendation System)

一个功能强大的多语言美股分析和推荐系统，采用模块化架构设计，支持多种分析策略和完整的测试框架。

A powerful multi-language US stock analysis and recommendation system with modular architecture design, supporting multiple analysis strategies and comprehensive testing framework.

## 功能特点 / Features

- 🌐 **多语言支持 / Multi-language Support**: 支持英文和中文界面切换，完整的国际化架构 / Support English and Chinese interface switching with complete internationalization architecture
- 📈 **实时股票数据获取 / Real-time Stock Data**: 使用yfinance库获取Yahoo Finance的实时股票数据 / Uses yfinance library to fetch real-time stock data from Yahoo Finance
- 🔍 **多种分析策略 / Multiple Analysis Strategies**: 
  - 技术分析策略 / Technical Analysis Strategy
  - 量化分析策略 / Quantitative Analysis Strategy  
  - AI/ML策略 / AI/ML Strategy
  - 综合策略 / Combined Strategy
- 🎯 **智能推荐引擎 / Smart Recommendation Engine**: 基于多种指标自动生成投资建议 / Automatically generates investment recommendations based on multiple indicators
- 📊 **风险评估系统 / Risk Assessment System**: 自动评估投资风险等级和信心度 / Automatic investment risk level and confidence assessment
- 📋 **详细分析报告 / Detailed Reports**: 生成完整的双语分析报告 / Generate comprehensive bilingual analysis reports
- 🧪 **完整测试框架 / Comprehensive Testing**: 单元测试、集成测试、性能测试全覆盖 / Full coverage with unit tests, integration tests, and performance tests

## 安装依赖 / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### 基本用法 / Basic Usage

```bash
# 英文版本 (默认) / English Version (Default)
python3 stock_recommender.py AAPL

# 中文版本 / Chinese Version
python3 stock_recommender.py AAPL --lang zh

# 指定分析策略 / Specify Analysis Strategy
python3 stock_recommender.py AAPL --strategy technical --lang en
python3 stock_recommender.py AAPL --strategy quantitative --lang zh
```

### 指定数据时间范围 / Specify Data Time Range

```bash
# 英文版本 / English Version
python3 stock_recommender.py TSLA --period 6mo --lang en

# 中文版本 / Chinese Version
python3 stock_recommender.py TSLA --period 6mo --lang zh
```

### 支持的分析策略 / Supported Analysis Strategies
- `technical`: 技术分析策略 / Technical Analysis Strategy
- `quantitative`: 量化分析策略 / Quantitative Analysis Strategy
- `ai`: AI/机器学习策略 / AI/Machine Learning Strategy
- `combined`: 综合策略(默认) / Combined Strategy (Default)

### 支持的时间范围 / Supported Time Periods
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

### 支持的语言 / Supported Languages
- `en`: English (英文)
- `zh`: Chinese (中文)

## 分析指标 / Analysis Indicators

### 技术指标 / Technical Indicators
- **移动平均线 / Moving Averages**: SMA20, SMA50
- **指数移动平均 / Exponential Moving Averages**: EMA12, EMA26
- **MACD**: 趋势跟踪指标 / Trend Following Indicator
- **RSI**: 相对强弱指数 (超买超卖指标) / Relative Strength Index (Overbought/Oversold Indicator)
- **布林带 / Bollinger Bands**: 价格波动区间 / Price Volatility Range
- **成交量分析 / Volume Analysis**: 成交量异常检测 / Volume Anomaly Detection

### 推荐策略 / Recommendation Strategies
- **强烈买入 / Strong Buy**: 综合评分 >= 50 / Composite Score >= 50
- **买入 / Buy**: 综合评分 >= 25 / Composite Score >= 25
- **持有 / Hold**: 综合评分 -25 到 25 / Composite Score -25 to 25
- **卖出 / Sell**: 综合评分 -50 到 -25 / Composite Score -50 to -25
- **强烈卖出/做空 / Strong Sell/Short**: 综合评分 <= -50 / Composite Score <= -50

## 示例输出 / Example Output

### 中文版本 / Chinese Version

```
============================================================
           美股投资策略推荐报告
============================================================

股票代码: AAPL
当前价格: $254.43
价格变动: $-1.65 (-0.64%)
分析时间: 2025-09-24 22:39:20

============================================================
技术分析
============================================================
趋势分析: 上升趋势
动量指标: RSI中性 | MACD看涨
成交量分析: 成交量正常

关键技术指标:
- RSI: 66.81
- MACD: 6.3762
- SMA 20: $237.15
- SMA 50: $225.65

============================================================
投资建议
============================================================
推荐操作: 强烈买入
信心等级: 高
风险评级: 低风险
综合评分: 50/100

分析依据:
1. 价格在20日均线上方
2. 短期均线上穿长期均线
3. MACD金叉看涨
4. 价格触及布林带上轨
```

### English Version / 英文版本

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

## 项目结构 / Project Structure

```
stock recommander/
├── stock_recommender.py          # 主程序入口 / Main program entry
├── requirements.txt              # 依赖包列表 / Dependencies list
├── setup.cfg                     # 项目配置 / Project configuration
├── run_ci_tests.sh              # CI测试脚本 / CI test script
├── README.md                    # 项目文档 / Project documentation
├── src/                         # 源代码目录 / Source code directory
│   ├── __init__.py             # 包初始化 / Package initialization
│   ├── analyzers/              # 股票分析器模块 / Stock analyzer modules
│   │   ├── __init__.py
│   │   └── stock_analyzer.py   # 核心股票数据分析 / Core stock data analysis
│   ├── engines/                # 推荐引擎模块 / Recommendation engine modules
│   │   ├── __init__.py
│   │   ├── recommendation_engine.py  # 推荐引擎 / Recommendation engine
│   │   └── strategy_manager.py      # 策略管理器 / Strategy manager
│   ├── strategies/             # 分析策略模块 / Analysis strategy modules
│   │   ├── __init__.py
│   │   ├── base_strategy.py    # 基础策略类 / Base strategy class
│   │   ├── technical_strategy.py   # 技术分析策略 / Technical analysis strategy
│   │   ├── quantitative_strategy.py # 量化分析策略 / Quantitative analysis strategy
│   │   └── aiml_strategy.py    # AI/ML分析策略 / AI/ML analysis strategy
│   ├── languages/              # 多语言支持模块 / Multi-language support modules
│   │   ├── __init__.py
│   │   ├── config.py          # 语言配置管理 / Language configuration management
│   │   ├── en.py             # 英文文本资源 / English text resources
│   │   └── zh.py             # 中文文本资源 / Chinese text resources
│   └── utils/                  # 工具模块 / Utility modules
│       ├── __init__.py
│       └── formatters.py      # 格式化工具 / Formatting utilities
├── tests/                      # 测试套件 / Test suite
│   ├── __init__.py
│   ├── run_tests.py           # 测试运行器 / Test runner
│   ├── test_stock_analyzer.py  # 股票分析器测试 / Stock analyzer tests
│   ├── test_strategies.py     # 策略测试 / Strategy tests
│   ├── test_engines.py        # 引擎测试 / Engine tests
│   ├── test_integration.py    # 集成测试 / Integration tests
│   ├── test_language_config.py # 语言配置测试 / Language config tests
│   ├── test_utils.py          # 测试工具 / Test utilities
│   └── test_utils.py          # 测试配置和模拟数据 / Test configuration and mock data
└── .github/
    └── copilot-instructions.md
```

### 核心架构设计 / Core Architecture Design

#### 模块化分层架构 / Modular Layered Architecture

1. **表示层 / Presentation Layer**: `stock_recommender.py`
   - 命令行界面和用户交互 / Command-line interface and user interaction
   - 参数解析和输出格式化 / Parameter parsing and output formatting

2. **业务逻辑层 / Business Logic Layer**: `src/engines/`
   - 推荐引擎协调各种策略 / Recommendation engine coordinates various strategies
   - 策略管理和结果聚合 / Strategy management and result aggregation

3. **分析策略层 / Analysis Strategy Layer**: `src/strategies/`
   - 可插拔的分析策略实现 / Pluggable analysis strategy implementations
   - 技术分析、量化分析、AI/ML分析 / Technical, quantitative, AI/ML analysis

4. **数据访问层 / Data Access Layer**: `src/analyzers/`
   - 股票数据获取和预处理 / Stock data fetching and preprocessing
   - 技术指标计算 / Technical indicator calculations

5. **基础设施层 / Infrastructure Layer**: `src/languages/`, `src/utils/`
   - 多语言支持和工具函数 / Multi-language support and utility functions

#### 多语言国际化架构 / Multi-language Internationalization Architecture

项目采用完整的国际化架构设计：
The project uses a complete internationalization architecture design:

- **`src/languages/config.py`**: 语言配置管理核心 / Language configuration management core
- **`src/languages/en.py`**: 英文资源文件 / English resource file
- **`src/languages/zh.py`**: 中文资源文件 / Chinese resource file
- **`LanguageConfig`类**: 动态语言切换和资源加载 / Dynamic language switching and resource loading

**架构优势 / Architecture Advantages:**
- ✅ **完全解耦 / Complete Decoupling**: 代码逻辑与文本资源分离 / Code logic separated from text resources
- ✅ **类型安全 / Type Safety**: 所有文本键值都有类型检查 / All text keys have type checking
- ✅ **易于扩展 / Easy Extension**: 新增语言只需添加资源文件 / Add new languages by adding resource files
- ✅ **运行时切换 / Runtime Switching**: 支持程序运行时语言切换 / Support runtime language switching

## 测试框架 / Testing Framework

项目包含完整的测试体系：
The project includes a comprehensive testing system:

```bash
# 运行完整的CI测试套件 / Run complete CI test suite
bash run_ci_tests.sh

# 运行特定测试模块 / Run specific test modules  
python3 -m pytest tests/test_strategies.py
python3 -m pytest tests/test_integration.py
```

**测试覆盖范围 / Test Coverage:**
- 📋 **单元测试 / Unit Tests**: 各个模块的独立功能测试 / Independent functionality tests for each module
- 🔗 **集成测试 / Integration Tests**: 模块间协作和端到端测试 / Inter-module collaboration and end-to-end tests
- 🚀 **性能测试 / Performance Tests**: 系统响应时间和资源使用测试 / System response time and resource usage tests
- 🧪 **烟雾测试 / Smoke Tests**: 核心功能快速验证 / Quick verification of core functionality
- 🌐 **多语言测试 / Multi-language Tests**: 国际化功能完整性测试 / Internationalization functionality integrity tests

## 开发和部署 / Development and Deployment

### 开发环境设置 / Development Environment Setup

```bash
# 克隆项目 / Clone project
git clone https://github.com/lvyongyu/us-stock-recommender.git
cd "stock recommander"

# 安装依赖 / Install dependencies
pip3 install -r requirements.txt

# 运行测试 / Run tests
bash run_ci_tests.sh

# 运行程序 / Run program
python3 stock_recommender.py AAPL --lang zh
```

### 推荐开发环境 / Recommended Development Environment

- **Python**: 3.8+ (推荐 3.9+ / Recommended 3.9+)
- **IDE**: VS Code, PyCharm, 或其他支持Python的IDE / VS Code, PyCharm, or other Python-supported IDE
- **Git**: 最新版本 / Latest version
- **操作系统 / OS**: macOS, Linux, Windows (推荐类Unix系统 / Unix-like systems recommended)

⚠️ **重要提醒 / Important Notice**: 本软件仅供学习和参考用途，不构成投资建议。股市有风险，投资需谨慎！使用本软件进行投资决策的风险由用户自行承担。

⚠️ **Important Notice**: This software is for educational and reference purposes only and does not constitute investment advice. Stock market involves risks, please invest cautiously! The risks of making investment decisions using this software are borne by the user.

## 技术栈 / Tech Stack

### 核心依赖 / Core Dependencies
- **Python 3.8+**: 主要编程语言 / Main programming language
- **yfinance**: 股票数据获取 / Stock data fetching
- **pandas**: 数据处理和分析 / Data processing and analysis  
- **numpy**: 数值计算和技术指标 / Numerical computation and technical indicators

### 开发工具 / Development Tools
- **unittest**: 单元测试框架 / Unit testing framework
- **argparse**: 命令行参数解析 / Command-line argument parsing
- **datetime**: 时间和日期处理 / Time and date processing

### 可选扩展 / Optional Extensions
- **matplotlib & seaborn**: 数据可视化 / Data visualization
- **scikit-learn**: 机器学习算法 / Machine learning algorithms
- **ta-lib**: 高级技术分析库 / Advanced technical analysis library

## 免责声明 / Disclaimer

## 后续扩展计划 / Future Enhancement Plans

### 近期计划 / Short-term Plans
- [ ] 📈 添加图表可视化功能 / Add chart visualization features
- [ ] 🔔 实时价格监控和预警 / Real-time price monitoring and alerts
- [ ] 📊 增加更多技术指标 / Add more technical indicators
- [ ] 🧠 改进AI/ML策略算法 / Improve AI/ML strategy algorithms

### 中期计划 / Medium-term Plans
- [ ] 🎯 支持多股票组合分析 / Support multi-stock portfolio analysis
- [ ] 📰 集成新闻情绪分析 / Integrate news sentiment analysis
- [ ] 🔄 添加回测功能 / Add backtesting functionality
- [ ] 🌐 创建Web界面 / Create web interface

### 长期计划 / Long-term Plans
- [ ] 📱 移动应用开发 / Mobile app development
- [ ] 🤖 高级AI预测模型 / Advanced AI prediction models
- [ ] ☁️ 云端部署和API服务 / Cloud deployment and API services
- [ ] 🔗 集成更多数据源 / Integrate more data sources

## 贡献指南 / Contributing Guidelines

### 贡献方式 / How to Contribute
1. Fork 本项目 / Fork this project
2. 创建特性分支 / Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 提交更改 / Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 / Push to the branch (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request / Open a Pull Request

### 开发规范 / Development Standards
- 遵循 PEP 8 Python 编码规范 / Follow PEP 8 Python coding standards
- 所有新功能必须包含测试 / All new features must include tests
- 保持测试覆盖率在90%以上 / Maintain test coverage above 90%
- 更新相关文档 / Update relevant documentation
- 确保CI测试通过 / Ensure CI tests pass

欢迎提交Issue和Pull Request来改进这个项目！
Welcome to submit Issues and Pull Requests to improve this project!

## 许可证 / License

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
