"""
中文语言资源文件 - 美股推荐系统
Chinese language resources for US Stock Recommendation System
"""

# 中文文本资源
TEXTS = {
    # 通用界面
    "analyzing": "正在分析股票: {}...",
    "error": "错误: {}",
    
    # 数据获取错误
    "no_data_found": "无法获取股票 {} 的数据",
    "fetch_data_failed": "获取数据失败: {}",
    "data_required": "请先获取股票数据",
    
    # 报告标题
    "report_title": "美股投资策略推荐报告",
    "stock_code": "股票代码",
    "current_price": "当前价格",
    "price_change": "价格变动",
    "analysis_time": "分析时间",
    
    # 技术分析
    "technical_analysis": "技术分析",
    "trend_analysis": "趋势分析",
    "momentum_indicators": "动量指标",
    "volume_analysis": "成交量分析",
    "key_metrics": "关键技术指标",
    
    # 投资建议
    "investment_advice": "投资建议",
    "recommended_action": "推荐操作",
    "confidence_level": "信心等级",
    "risk_rating": "风险评级",
    "composite_score": "综合评分",
    "analysis_basis": "分析依据",
    
    # 操作建议
    "strong_buy": "强烈买入",
    "buy": "买入",
    "hold": "持有",
    "sell": "卖出",
    "strong_sell": "强烈卖出/做空",
    
    # 信心等级
    "high": "高",
    "medium": "中等",
    "low": "低",
    
    # 风险等级
    "low_risk": "低风险",
    "medium_risk": "中等风险",
    "high_risk": "高风险",
    
    # 趋势方向
    "uptrend": "上升趋势",
    "downtrend": "下降趋势",
    "sideways": "横盘整理",
    
    # 动量指标
    "rsi_neutral": "RSI中性",
    "rsi_overbought": "RSI超买",
    "rsi_oversold": "RSI超卖",
    "macd_bullish": "MACD看涨",
    "macd_bearish": "MACD看跌",
    
    # 成交量状态
    "volume_normal": "成交量正常",
    "volume_high": "成交量放大",
    "volume_low": "成交量萎缩",
    
    # 技术分析信号
    "price_above_sma20": "价格在20日均线上方",
    "price_below_sma20": "价格在20日均线下方",
    "sma_golden_cross": "短期均线上穿长期均线",
    "sma_death_cross": "短期均线下穿长期均线",
    "macd_golden_cross": "MACD金叉看涨",
    "macd_death_cross": "MACD死叉看跌",
    "rsi_overbought_signal": "RSI超买，可能回调",
    "rsi_oversold_signal": "RSI超卖，可能反弹",
    "rsi_neutral_zone": "RSI中性区域",
    "bollinger_upper": "价格触及布林带上轨",
    "bollinger_lower": "价格触及布林带下轨",
    
    # 免责声明
    "disclaimer": "免责声明: 本分析仅供参考，投资有风险，决策需谨慎！",
    
    # 命令行帮助
    "help_symbol": "股票代码 (例如: AAPL, TSLA, MSFT)",
    "help_period": "数据时间范围 (默认: 1y)",
    "help_language": "语言: en (英文) 或 zh (中文) (默认: en)",
    "help_description": "US Stock Recommendation System / 美股推荐系统",
    "help_strategy": "交易策略: technical (技术指标), quantitative (量化模型), ai (AI/机器学习), 或 all (全部) (默认: all)",
    
    # 策略名称
    "strategy_technical": "技术指标分析",
    "strategy_quantitative": "量化模型分析", 
    "strategy_ai": "AI/机器学习分析",
    "strategy_combined": "综合策略分析",
    
    # 技术策略推荐理由
    "strategy_rsi_oversold": "RSI({:.1f})超卖，潜在买入机会",
    "strategy_rsi_overbought": "RSI({:.1f})超买，潜在卖出压力", 
    "strategy_rsi_neutral": "RSI({:.1f})中性区域，适度信号",
    "strategy_macd_strong_bullish": "MACD金叉且在零轴上方，强烈看涨趋势",
    "strategy_macd_bullish": "MACD金叉，看涨动量",
    "strategy_macd_strong_bearish": "MACD死叉且在零轴下方，强烈看跌趋势",
    "strategy_macd_bearish": "MACD死叉，看跌动量",
    "strategy_ma_strong_uptrend": "价格突破短期和长期均线，强烈上升趋势",
    "strategy_ma_above_short": "价格突破短期均线，正向动量",
    "strategy_ma_strong_downtrend": "价格跌破所有均线，强烈下降趋势", 
    "strategy_ma_below_short": "价格跌破短期均线，负向动量",
    "strategy_bb_oversold": "价格跌破布林带下轨，潜在超卖",
    "strategy_bb_overbought": "价格突破布林带上轨，潜在超买",
    "strategy_bb_above_middle": "价格在布林带中轨上方，看涨偏向",
    
    # 量化策略推荐理由
    "strategy_momentum_strong": "强劲动量：{:.1f}%(5日)，{:.1f}%(20日)，看涨趋势",
    "strategy_momentum_positive": "正向动量：{:.1f}%(5日)，{:.1f}%(20日)，上升偏向",
    "strategy_momentum_weak": "疲弱动量：{:.1f}%(5日)，{:.1f}%(20日)，看跌趋势", 
    "strategy_momentum_negative": "负向动量：{:.1f}%(5日)，{:.1f}%(20日)，下降偏向",
    "strategy_volatility_low": "低波动环境，有利于趋势延续",
    "strategy_volatility_high": "高波动环境，风险增加",
    "strategy_volume_surge_bullish": "成交量放大({:.1f}倍)伴随正向价格行动",
    "strategy_volume_surge_bearish": "成交量放大({:.1f}倍)伴随负向价格行动",
    "strategy_volume_low": "成交量低于平均水平，缺乏信心",
    "strategy_mean_reversion_oversold": "价格低于均值{:.1f}%，潜在均值回归机会", 
    "strategy_mean_reversion_overbought": "价格高于均值{:.1f}%，潜在均值回归风险",
    "strategy_mean_reversion_fair": "基于均值回归模型，价格接近合理价值",
    
    # AI/ML策略推荐理由
    "strategy_ml_rsi_oversold": "机器学习模型检测到RSI超卖状态",
    "strategy_ml_rsi_overbought": "机器学习模型检测到RSI超买状态",
    "strategy_ml_macd_bullish": "机器学习模型识别出MACD看涨形态",
    "strategy_ml_macd_bearish": "机器学习模型识别出MACD看跌形态", 
    "strategy_ml_bullish_prediction": "AI预测：{:.0f}%置信度看涨趋势",
    "strategy_ml_bearish_prediction": "AI预测：{:.0f}%置信度看跌趋势",
    "strategy_ml_neutral_prediction": "AI预测显示中性/横盘趋势",
    "strategy_ml_fallback": "机器学习分析不可用，使用技术分析备选方案",
    
    # 综合策略
    "strategy_consensus_strong": "多种策略强烈共识",
    "strategy_consensus_moderate": "多种策略适度共识", 
    "strategy_consensus_mixed": "不同策略信号不一致",
    "strategy_weight_technical": "技术分析权重：{}%",
    "strategy_weight_quantitative": "量化模型权重：{}%", 
    "strategy_weight_ai": "AI/机器学习权重：{}%"
}
