# 🎮 模拟投资系统 (Simulation Trading System)

## � 最新更新：真实股票数据支持！

✨ **系统现已支持真实股票数据！**
- 实时股价从 Yahoo Finance 获取
- 历史回测使用真实历史数据
- 网络连接失败时自动降级到模拟数据

## �📋 概述

基于现有股票推荐系统的模拟投资功能，让用户可以在无风险环境下练习投资策略、测试交易想法和学习投资知识。

## 🏗️ 系统架构

### 核心模块

```
src/simulation/
├── models.py              # 数据模型定义
├── account_manager.py     # 账户管理
├── trader.py             # 虚拟交易引擎
├── backtest_engine.py    # 历史回测引擎
├── web_integration.py    # Web界面集成
└── __init__.py          # 模块初始化
```

### 数据模型

- **SimulationAccount**: 模拟账户信息
- **VirtualTransaction**: 虚拟交易记录
- **VirtualPosition**: 虚拟持仓
- **TransactionType**: 交易类型枚举
- **OrderType**: 订单类型枚举

## 🎯 主要功能

### 1. 模拟账户管理
- ✅ 创建多个模拟账户
- ✅ 虚拟资金管理（初始$100,000）
- ✅ 账户余额和总资产跟踪
- ✅ 交易历史记录

### 2. 虚拟交易
- ✅ 市价买入/卖出
- ✅ 交易验证（资金、持仓检查）
- ✅ **真实股票价格获取** (Yahoo Finance)
- ✅ 手续费计算（0.1%）

### 3. 投资组合跟踪
- ✅ 持仓股票管理
- ✅ 平均成本计算
- ✅ 实时盈亏计算
- ✅ 投资组合总价值

### 4. 历史回测
- ✅ 多股票组合回测
- ✅ 多种投资策略
- ✅ **真实历史数据回测** (Yahoo Finance)
- ✅ 绩效指标计算
- ✅ 收益曲线图表

### 5. 自动交易 (NEW!)
- ✅ **基于推荐的自动交易** - 根据投资组合分析自动执行买入/卖出
- ✅ **智能资金分配** - 自动为推荐买入的股票分配可用资金
- ✅ **投资组合再平衡** - 支持目标分配比例的自动再平衡
- ✅ **推荐引擎集成** - 与现有股票推荐系统完全集成

## 🚀 快速开始

### 环境要求
- Python 3.8+
- yfinance 库（用于获取真实股票数据）
- 网络连接（用于实时数据获取）

### 运行演示

```bash
cd /Users/Eric/stock recommander
python demo_simulation.py          # 基础模拟交易演示
python demo_automated_trading.py   # 自动交易演示 (NEW!)
```

**注意**: 演示脚本现在使用真实的股票价格和历史数据，确保网络连接正常。

### Web界面集成

将 `src/simulation/web_integration.py` 中的代码集成到 `portfolio_app.py` 中：

```python
# 在portfolio_app.py中添加
from src.simulation.account_manager import SimulationAccountManager
from src.simulation.trader import VirtualTrader
from src.simulation.backtest_engine import BacktestEngine

# 初始化组件
simulation_manager = SimulationAccountManager()
virtual_trader = VirtualTrader(simulation_manager)
backtest_engine = BacktestEngine()

# 添加侧边栏菜单
simulation_page = add_simulation_sidebar()

# 根据选择显示不同页面
if simulation_page == "账户管理":
    show_simulation_accounts()
elif simulation_page == "虚拟交易":
    show_virtual_trading()
elif simulation_page == "历史回测":
    show_backtesting()
```

## 📊 技术指标

### 数据源
- **实时价格**: Yahoo Finance API (yfinance库)
- **历史数据**: Yahoo Finance 历史股价数据
- **备用方案**: 网络连接失败时自动使用模拟数据

### 绩效指标计算

- **总收益率**: `(期末价值 - 初始资金) / 初始资金 × 100%`
- **年化收益率**: `((期末价值/初始资金)^(1/年数) - 1) × 100%`
- **最大回撤**: `最高点到最低点的最大跌幅`
- **夏普比率**: `(年化收益率 - 无风险利率) / 年化波动率`
- **胜率**: `盈利交易天数 / 总交易天数`

### 风险控制

- **资金充足性检查**: 买入前验证可用资金
- **持仓验证**: 卖出前检查股票数量
- **价格合理性**: 使用实时股价进行交易

## 🎮 使用场景

### 1. 投资学习
- 新手练习基本交易操作
- 学习投资策略和风险管理
- 理解市场波动和投资心理

### 2. 策略测试
- 在历史数据上测试投资策略
- 比较不同策略的绩效表现
- 优化投资组合配置

### 3. 风险教育
- 体验市场下跌的影响
- 学习分散投资的重要性
- 理解交易成本的影响

## 🔧 扩展计划

### 短期目标
- [ ] 限价订单支持
- [ ] 更多技术指标集成
- [ ] **自动交易策略优化** (NEW!)
- [ ] 投资组合再平衡建议

### 长期规划
- [ ] 多用户系统
- [ ] 实时模拟交易竞赛
- [ ] AI投资建议集成
- [ ] 社交功能（分享策略）

## 📈 集成优势

### 与现有系统的完美集成
- 复用 `StockInfoManager` 获取实时价格
- 利用 `PortfolioAnalyzer` 进行组合分析
- 集成 `RecommendationEngine` 提供交易建议

### 数据一致性
- 使用相同的股票数据源
- 统一的分析方法和指标
- 一致的用户体验

## 🎯 核心价值

1. **零风险学习**: 在虚拟环境中练习投资
2. **策略验证**: 历史回测验证投资想法
3. **技能提升**: 逐步掌握投资知识
4. **决策支持**: 数据驱动的投资决策
5. **自动交易**: 基于AI推荐的自动化投资执行 (NEW!)

---

*这个模拟投资系统让每个人都能成为更好的投资者！* 🚀📈