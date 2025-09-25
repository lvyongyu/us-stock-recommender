# Portfolio Management System - Web Interface

🎯 **现代化的投资组合管理系统** - 基于Streamlit构建的Web界面，提供直观易用的投资组合管理和分析功能。

## 🚀 快速开始

### 启动Web界面

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Streamlit应用
streamlit run portfolio_app.py
```

访问 http://localhost:8501 开始使用！

### 或者运行演示程序

```bash
# 运行完整功能演示
python3 demo_portfolio.py
```

## ✨ 主要功能

### 🏠 Dashboard（仪表板）
- 📊 投资组合总览和关键指标
- 📈 投资组合性能比较
- 🎯 快速统计信息
- 📋 最新投资组合状态

### 💼 Portfolio Management（投资组合管理）
- ✅ **创建投资组合** - 支持多种投资策略（保守型、平衡型、激进型）
- ✏️ **编辑投资组合** - 修改描述、策略、添加/删除股票
- 📊 **持仓可视化** - 饼图显示资产分配
- ⚖️ **智能再平衡** - 自动调整至目标权重

### 🔍 Portfolio Analysis（投资组合分析）
- 💡 **智能推荐** - 基于多因子分析的买卖建议
- 📊 **关键指标** - 预期收益、风险评分、多元化程度
- 📈 **个股分析** - 每只股票的详细分析和推荐
- ⚠️ **风险评估** - 全面的风险因子识别
- ⚖️ **再平衡建议** - 智能权重调整建议

### 🆚 Portfolio Comparison（投资组合比较）
- 📊 **性能对比** - 收益、风险、多元化对比
- 📈 **可视化图表** - 风险-收益散点图
- 💡 **决策支持** - 基于数据的投资组合选择建议

### ⚙️ Settings（设置）
- 🌐 **多语言支持** - 中英文切换
- 💾 **数据管理** - 缓存清理、数据导出
- ℹ️ **系统信息** - 版本和统计信息

## 🛠️ 技术特性

### 核心功能
- ✅ **Portfolio Creation** - 投资组合创建和配置
- ✅ **Stock Management** - 股票持仓跟踪和权重管理
- ✅ **Real-time Analysis** - 实时投资组合分析
- ✅ **Risk Assessment** - 多维度风险评估
- ✅ **Smart Rebalancing** - 智能再平衡建议
- ✅ **Multi-language** - 中英文双语支持

### 数据可视化
- 📊 **Interactive Charts** - 基于Plotly的交互式图表
- 🥧 **Holdings Distribution** - 持仓分布饼图
- 📈 **Risk-Return Analysis** - 风险收益散点图
- 📊 **Weight Comparison** - 当前vs目标权重对比

### 数据持久化
- 💾 **JSON Storage** - 本地JSON文件存储
- 🔄 **Auto-backup** - 自动备份机制
- 📁 **File Management** - 完整的文件管理系统

## 🎯 使用指南

### 1. 创建第一个投资组合
1. 访问 "💼 Portfolio Management" 页面
2. 在 "📝 Create Portfolio" 标签页中填写投资组合信息
3. 选择投资策略（保守型/平衡型/激进型）
4. 点击 "Create Portfolio"

### 2. 添加股票持仓
1. 在 "✏️ Edit Portfolio" 标签页选择投资组合
2. 在 "Add New Stock" 表单中输入：
   - 股票代码（如 AAPL）
   - 当前权重（%）
   - 目标权重（%）
   - 投资备注
3. 点击 "Add Stock"

### 3. 分析投资组合
1. 访问 "🔍 Portfolio Analysis" 页面
2. 选择要分析的投资组合
3. 查看详细分析结果：
   - 总体推荐和置信度
   - 关键指标（收益、风险、多元化）
   - 个股分析和推荐
   - 风险评估和因子
   - 再平衡建议

### 4. 比较投资组合
1. 访问 "🆚 Portfolio Comparison" 页面
2. 选择两个投资组合进行比较
3. 查看详细对比分析和可视化图表

## 📊 系统架构

```
portfolio_app.py          # Streamlit Web界面
├── Dashboard             # 仪表板和总览
├── Portfolio Management  # 投资组合CRUD操作
├── Portfolio Analysis    # 深度分析和推荐
├── Portfolio Comparison  # 投资组合比较
└── Settings             # 配置和设置

src/portfolio/            # 核心业务逻辑
├── models.py            # 数据模型
├── manager.py           # 投资组合管理器
├── analyzer.py          # 分析引擎
├── file_manager.py      # 文件管理
└── exceptions.py        # 异常处理

demo_portfolio.py        # 完整功能演示
```

## 🔧 配置说明

### 数据存储位置
```
~/.stock_recommender/
└── portfolios/
    ├── portfolio_name.json    # 投资组合数据
    └── backups/              # 自动备份
```

### 支持的投资策略
- **Conservative（保守型）** - 低风险、稳定收益
- **Balanced（平衡型）** - 中等风险、平衡收益  
- **Aggressive（激进型）** - 高风险、高收益潜力

### 分析功能
- **期望收益计算** - 基于历史数据和模型预测
- **风险评分** - 多因子风险模型
- **多元化评估** - 持仓集中度和行业分布分析
- **再平衡建议** - 基于目标权重的智能调整

## 🚀 高级功能

### 批量操作
- 批量添加股票
- 批量权重调整
- 批量分析多个投资组合

### 分析缓存
- 自动缓存分析结果（30分钟有效期）
- 可选择强制刷新获取最新分析
- 内存优化和性能提升

### 多语言支持
- 界面：英文
- 分析结果：中英文切换
- 风险评级和推荐本地化

## 📈 示例投资组合

系统包含了以下示例，演示完整功能：

### 科技成长型投资组合
```
Strategy: Aggressive
Holdings:
- AAPL: 25% (iPhone生态系统领导者)
- MSFT: 25% (云计算和企业软件)
- GOOGL: 25% (搜索和AI技术)
- TSLA: 25% (电动汽车先驱)
```

### 平衡型投资组合
```
Strategy: Conservative  
Holdings:
- VTI: 40% (美国股市总体)
- BND: 30% (债券市场)
- VEA: 20% (国际发达市场)
- VWO: 10% (新兴市场)
```

## 🎉 总结

这个投资组合管理系统提供了：

✅ **完整的投资组合生命周期管理**
✅ **基于数据驱动的分析和推荐**  
✅ **现代化的Web界面和可视化**
✅ **多语言支持和本地化**
✅ **可靠的数据持久化和备份**

**开始您的投资组合管理之旅！** 🚀

---

*系统版本: 1.0.0 | 构建于: Streamlit + Python | 支持: 多投资组合分析管理*