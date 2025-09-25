"""
Stock symbol correction and delisting configuration

This configuration file contains mappings for common stock symbol corrections
and information about delisted/acquired stocks. This data should be regularly
updated to reflect market changes.
"""

# Smart stock symbol correction mapping
# Common stock symbol corrections mapping
SYMBOL_CORRECTIONS = {
    'TESLA': 'TSLA',
    'APPLE': 'AAPL',
    'MICROSOFT': 'MSFT',
    'GOOGLE': 'GOOGL',
    'ALPHABET': 'GOOGL',
    'AMAZON': 'AMZN',
    'ADOBE': 'ADBE',
    'INTEL': 'INTC',
    'CISCO': 'CSCO',
    'FACEBOOK': 'META',
    'META': 'META',
    'NETFLIX': 'NFLX',
    'PAYPAL': 'PYPL',
    'NVIDIA': 'NVDA',
    'ORACLE': 'ORCL',
    'QUALCOMM': 'QCOM',
    'SALESFORCE': 'CRM',
    'SHOPIFY': 'SHOP'
}

# 已知退市/被收购股票信息
# Known delisted/acquired stocks information
DELISTED_STOCKS = {
    # 2023年银行业危机
    'SIVB': {
        'en': 'Silicon Valley Bank collapsed (2023)',
        'zh': 'Silicon Valley Bank已倒闭 (2023)'
    },
    'FRC': {
        'en': 'First Republic Bank collapsed (2023)', 
        'zh': 'First Republic Bank已倒闭 (2023)'
    },
    'PACW': {
        'en': 'Affected by banking crisis, trading suspended',
        'zh': '受银行业危机影响停牌'
    },
    
    # 收购案例
    'SPLK': {
        'en': 'Acquired by Cisco (2021)',
        'zh': '已被Cisco收购 (2021)'
    },
    'VMW': {
        'en': 'Acquired by Broadcom (2023)',
        'zh': '已被Broadcom收购 (2023)'
    },
    'PXD': {
        'en': 'Acquired by ExxonMobil (2023)',
        'zh': '已被ExxonMobil收购 (2023)'
    },
    
    # 业务重组
    'WAB': {
        'en': 'Business restructuring impact',
        'zh': '业务重组影响'
    },
    'HES': {
        'en': 'Partial asset divestiture affecting trading',
        'zh': '部分资产剥离影响交易'
    }
}

def get_symbol_correction(symbol: str) -> str:
    """
    获取股票代码纠错建议
    Get symbol correction suggestion
    
    Args:
        symbol: 输入的股票代码 / Input stock symbol
        
    Returns:
        纠正后的股票代码，如果没有找到则返回原代码
        Corrected symbol, or original if no correction found
    """
    return SYMBOL_CORRECTIONS.get(symbol.upper(), symbol)


def get_delisted_info(symbol: str, language: str = 'en') -> str:
    """
    获取退市股票信息
    Get delisted stock information
    
    Args:
        symbol: 股票代码 / Stock symbol
        language: 语言 ('en' 或 'zh') / Language ('en' or 'zh')
        
    Returns:
        退市信息，如果没有找到则返回None
        Delisting information, or None if not found
    """
    delisted_info = DELISTED_STOCKS.get(symbol.upper())
    if delisted_info:
        return delisted_info.get(language, delisted_info.get('en', ''))
    return None


def is_known_correction(symbol: str) -> bool:
    """
    检查是否是已知的需要纠错的股票代码
    Check if symbol is a known correction case
    
    Args:
        symbol: 股票代码 / Stock symbol
        
    Returns:
        是否需要纠错 / Whether correction is needed
    """
    return symbol.upper() in SYMBOL_CORRECTIONS


def is_known_delisted(symbol: str) -> bool:
    """
    检查是否是已知的退市股票
    Check if symbol is a known delisted stock
    
    Args:
        symbol: 股票代码 / Stock symbol
        
    Returns:
        是否是已知退市股票 / Whether it's a known delisted stock
    """
    return symbol.upper() in DELISTED_STOCKS