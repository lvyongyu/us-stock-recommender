# 美股推荐软件 (US Stock Recommendation System)

一个支持多语言的美股分析和推荐系统，能够分析股票数据并生成投资策略建议（买入、卖出、做空等）。

A multi-language US stock analysis and recommendation system that analyzes stock data and generates investment strategy recommendations (buy, sell, short, etc.).

## 功能特点 / Features

- 🌐 **多语言支持 / Multi-language Support**: 支持英文和中文界面切换 / Support English and Chinese interface switching
- 📈 **实时股票数据获取 / Real-time Stock Data**: 使用yfinance库获取Yahoo Finance的实时股票数据 / Uses yfinance library to fetch real-time stock data from Yahoo Finance
- 🔍 **技术指标分析 / Technical Analysis**: 支持多种技术指标分析（RSI、MACD、布林带、移动平均线等）/ Supports multiple technical indicators (RSI, MACD, Bollinger Bands, Moving Averages, etc.)
- 🎯 **智能推荐策略 / Smart Recommendations**: 基于技术分析自动生成买入、卖出、做空等投资建议 / Automatically generates buy, sell, short investment recommendations based on technical analysis
- 📊 **风险评估 / Risk Assessment**: 自动评估投资风险等级 / Automatic investment risk level assessment
- 📋 **详细分析报告 / Detailed Reports**: 生成完整的双语分析报告 / Generate comprehensive bilingual analysis reports

## 安装依赖 / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### 基本用法 / Basic Usage

```bash
# 英文版本 (默认) / English Version (Default)
python stock_recommender.py AAPL

# 中文版本 / Chinese Version
python stock_recommender.py AAPL --lang zh

# 英文版本（显式指定）/ English Version (Explicit)
python stock_recommender.py AAPL --lang en
```

### 指定数据时间范围 / Specify Data Time Range

```bash
# 英文版本 / English Version
python stock_recommender.py TSLA --period 6mo --lang en

# 中文版本 / Chinese Version
python stock_recommender.py TSLA --period 6mo --lang zh
```

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
├── stock_recommender.py    # 主程序文件 / Main program file
├── requirements.txt        # 依赖包列表 / Dependencies list
├── README.md              # 项目说明 / Project documentation
├── languages/             # 语言资源包 / Language resources package
│   ├── __init__.py       # 包初始化文件 / Package initialization
│   ├── en.py            # 英文文本资源 / English text resources
│   └── zh.py            # 中文文本资源 / Chinese text resources
└── .github/
    └── copilot-instructions.md
```

### 语言资源架构 / Language Resource Architecture

项目采用模块化的多语言架构，将所有文本资源分离到独立文件中：
The project uses a modular multi-language architecture with all text resources separated into independent files:

- **`languages/en.py`**: 包含所有英文文本常量 / Contains all English text constants
- **`languages/zh.py`**: 包含所有中文文本常量 / Contains all Chinese text constants  
- **`languages/__init__.py`**: 语言包导出模块 / Language package export module
- **`LanguageConfig`类**: 动态加载语言资源 / Dynamic language resource loader

这种设计的优势 / Advantages of this design:
- ✅ **易于维护 / Easy Maintenance**: 文本与代码分离 / Text separated from code
- ✅ **易于扩展 / Easy Extension**: 添加新语言只需新建资源文件 / Add new languages by creating resource files
- ✅ **代码简洁 / Clean Code**: 主程序逻辑更清晰 / Main program logic is clearer
- ✅ **版本控制友好 / Version Control Friendly**: 文本修改不影响代码 / Text changes don't affect code

## 免责声明 / Disclaimer

⚠️ **重要提醒 / Important Notice**: 本软件仅供学习和参考用途，不构成投资建议。股市有风险，投资需谨慎！使用本软件进行投资决策的风险由用户自行承担。

⚠️ **Important Notice**: This software is for educational and reference purposes only and does not constitute investment advice. Stock market involves risks, please invest cautiously! The risks of making investment decisions using this software are borne by the user.

## 技术栈 / Tech Stack

- **Python 3.8+**
- **yfinance**: 股票数据获取 / Stock data fetching
- **pandas**: 数据处理和分析 / Data processing and analysis  
- **numpy**: 数值计算 / Numerical computation
- **matplotlib & seaborn**: 数据可视化（可选扩展）/ Data visualization (optional extension)

## 后续扩展计划 / Future Enhancement Plans

- [ ] 添加图表可视化功能 / Add chart visualization features
- [ ] 支持多股票组合分析 / Support multi-stock portfolio analysis
- [ ] 增加更多技术指标 / Add more technical indicators
- [ ] 添加基本面分析 / Add fundamental analysis
- [ ] 支持自定义策略配置 / Support custom strategy configuration
- [ ] 添加回测功能 / Add backtesting functionality
- [ ] 创建Web界面 / Create web interface
- [ ] 添加实时监控和预警 / Add real-time monitoring and alerts

## 贡献 / Contributing

欢迎提交Issue和Pull Request来改进这个项目！
Welcome to submit Issues and Pull Requests to improve this project!

## 许可证 / License

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
