# 美股推荐软件

一个功能强大的多语言美股分析和推荐系统，采用模块化架构设计，支持多种分析策略和完整的测试框架。

## 📖 文档

- [🇺🇸 English](README.md)
- [🇨🇳 中文文档](README.zh.md) ← 当前页面

## 功能特点

- 🌐 **多语言支持**: 支持英文和中文界面切换，完整的国际化架构
- 📈 **实时股票数据获取**: 使用yfinance库获取Yahoo Finance的实时股票数据
- 🔍 **多种分析策略**: 
  - 技术分析策略
  - 量化分析策略  
  - AI/ML策略
  - 综合策略
- 🎯 **智能推荐引擎**: 基于多种指标自动生成投资建议
- 📊 **风险评估系统**: 自动评估投资风险等级和信心度
- 📋 **详细分析报告**: 生成完整的双语分析报告
- 🧪 **完整测试框架**: 单元测试、集成测试、性能测试全覆盖

## 安装依赖

```bash
pip3 install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 英文版本 (默认)
python3 stock_recommender.py AAPL

# 中文版本
python3 stock_recommender.py AAPL --lang zh

# 指定分析策略
python3 stock_recommender.py AAPL --strategy technical --lang en
python3 stock_recommender.py AAPL --strategy quantitative --lang zh
```

### 指定数据时间范围

```bash
# 英文版本
python3 stock_recommender.py TSLA --period 6mo --lang en

# 中文版本
python3 stock_recommender.py TSLA --period 6mo --lang zh
```

### 支持的分析策略
- `technical`: 技术分析策略
- `quantitative`: 量化分析策略
- `ai`: AI/机器学习策略
- `combined`: 综合策略(默认)

### 支持的时间范围
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

### 支持的语言
- `en`: English (英文)
- `zh`: Chinese (中文)

## 分析指标

### 技术指标
- **移动平均线**: SMA20, SMA50
- **指数移动平均**: EMA12, EMA26
- **MACD**: 趋势跟踪指标
- **RSI**: 相对强弱指数 (超买超卖指标)
- **布林带**: 价格波动区间
- **成交量分析**: 成交量异常检测

### 推荐策略
- **强烈买入**: 综合评分 >= 50
- **买入**: 综合评分 >= 25
- **持有**: 综合评分 -25 到 25
- **卖出**: 综合评分 -50 到 -25
- **强烈卖出/做空**: 综合评分 <= -50

## 示例输出

### 中文版本

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

## 项目结构

```
stock recommander/
├── stock_recommender.py          # 主程序入口
├── requirements.txt              # 依赖包列表
├── setup.cfg                     # 项目配置
├── run_ci_tests.sh              # CI测试脚本
├── README.md                    # 项目文档 (英文)
├── README.zh.md                 # 中文文档
├── src/                         # 源代码目录
│   ├── __init__.py             # 包初始化
│   ├── analyzers/              # 股票分析器模块
│   │   ├── __init__.py
│   │   └── stock_analyzer.py   # 核心股票数据分析
│   ├── engines/                # 推荐引擎模块
│   │   ├── __init__.py
│   │   ├── recommendation_engine.py  # 推荐引擎
│   │   └── strategy_manager.py      # 策略管理器
│   ├── strategies/             # 分析策略模块
│   │   ├── __init__.py
│   │   ├── base_strategy.py    # 基础策略类
│   │   ├── technical_strategy.py   # 技术分析策略
│   │   ├── quantitative_strategy.py # 量化分析策略
│   │   └── aiml_strategy.py    # AI/ML分析策略
│   ├── languages/              # 多语言支持模块
│   │   ├── __init__.py
│   │   ├── config.py          # 语言配置管理
│   │   ├── en.py             # 英文文本资源
│   │   └── zh.py             # 中文文本资源
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       └── formatters.py      # 格式化工具
├── tests/                      # 测试套件
│   ├── __init__.py
│   ├── run_tests.py           # 测试运行器
│   ├── test_stock_analyzer.py  # 股票分析器测试
│   ├── test_strategies.py     # 策略测试
│   ├── test_engines.py        # 引擎测试
│   ├── test_integration.py    # 集成测试
│   ├── test_language_config.py # 语言配置测试
│   └── test_utils.py          # 测试配置和模拟数据
└── .github/
    └── copilot-instructions.md
```

## 核心架构设计

### 模块化分层架构

1. **表示层**: `stock_recommender.py`
   - 命令行界面和用户交互
   - 参数解析和输出格式化

2. **业务逻辑层**: `src/engines/`
   - 推荐引擎协调各种策略
   - 策略管理和结果聚合

3. **分析策略层**: `src/strategies/`
   - 可插拔的分析策略实现
   - 技术分析、量化分析、AI/ML分析

4. **数据访问层**: `src/analyzers/`
   - 股票数据获取和预处理
   - 技术指标计算

5. **基础设施层**: `src/languages/`, `src/utils/`
   - 多语言支持和工具函数

### 多语言国际化架构

项目采用完整的国际化架构设计：

- **`src/languages/config.py`**: 语言配置管理核心
- **`src/languages/en.py`**: 英文资源文件
- **`src/languages/zh.py`**: 中文资源文件
- **`LanguageConfig`类**: 动态语言切换和资源加载

**架构优势:**
- ✅ **完全解耦**: 代码逻辑与文本资源分离
- ✅ **类型安全**: 所有文本键值都有类型检查
- ✅ **易于扩展**: 新增语言只需添加资源文件
- ✅ **运行时切换**: 支持程序运行时语言切换

## 测试框架

项目包含完整的测试体系：

```bash
# 运行完整的CI测试套件
bash run_ci_tests.sh

# 运行特定测试模块  
python3 -m pytest tests/test_strategies.py
python3 -m pytest tests/test_integration.py
```

**测试覆盖范围:**
- 📋 **单元测试**: 各个模块的独立功能测试
- 🔗 **集成测试**: 模块间协作和端到端测试
- 🚀 **性能测试**: 系统响应时间和资源使用测试
- 🧪 **烟雾测试**: 核心功能快速验证
- 🌐 **多语言测试**: 国际化功能完整性测试

## 开发和部署

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/lvyongyu/us-stock-recommender.git
cd "stock recommander"

# 安装依赖
pip3 install -r requirements.txt

# 运行测试
bash run_ci_tests.sh

# 运行程序
python3 stock_recommender.py AAPL --lang zh
```

### 推荐开发环境

- **Python**: 3.8+ (推荐 3.9+)
- **IDE**: VS Code, PyCharm, 或其他支持Python的IDE
- **Git**: 最新版本
- **操作系统**: macOS, Linux, Windows (推荐类Unix系统)

## 技术栈

### 核心依赖
- **Python 3.8+**: 主要编程语言
- **yfinance**: 股票数据获取
- **pandas**: 数据处理和分析  
- **numpy**: 数值计算和技术指标

### 开发工具
- **unittest**: 单元测试框架
- **argparse**: 命令行参数解析
- **datetime**: 时间和日期处理

### 可选扩展
- **matplotlib & seaborn**: 数据可视化
- **scikit-learn**: 机器学习算法
- **ta-lib**: 高级技术分析库

## 免责声明

⚠️ **重要提醒**: 本软件仅供学习和参考用途，不构成投资建议。股市有风险，投资需谨慎！使用本软件进行投资决策的风险由用户自行承担。

## 后续扩展计划

### 近期计划
- [ ] 📈 添加图表可视化功能
- [ ] 🔔 实时价格监控和预警
- [ ] 📊 增加更多技术指标
- [ ] 🧠 改进AI/ML策略算法

### 中期计划
- [ ] 🎯 支持多股票组合分析
- [ ] 📰 集成新闻情绪分析
- [ ] 🔄 添加回测功能
- [ ] 🌐 创建Web界面

### 长期计划
- [ ] 📱 移动应用开发
- [ ] 🤖 高级AI预测模型
- [ ] ☁️ 云端部署和API服务
- [ ] 🔗 集成更多数据源

## 贡献指南

### 贡献方式
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 开发规范
- 遵循 PEP 8 Python 编码规范
- 所有新功能必须包含测试
- 保持测试覆盖率在90%以上
- 更新相关文档
- 确保CI测试通过

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件
