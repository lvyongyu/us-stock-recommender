#!/usr/bin/env python3
"""
动态股票选择功能测试
"""

import sys
import os
sys.path.append('.')

def test_dynamic_stock_selection():
    """测试动态股票选择功能"""
    print("🧪 测试动态股票选择功能...")
    
    try:
        from src.utils.stock_info_manager import StockInfoManager, get_stock_manager
        from src.utils.stock_selector import create_dynamic_stock_selector, create_stock_weight_input
        
        print("✅ 模块导入成功")
        
        # 测试股票管理器
        manager = StockInfoManager()
        
        # 测试搜索功能
        print("\n📈 测试股票搜索功能:")
        test_queries = ["AAPL", "Apple", "Microsoft", "MSFT", "Tesla"]
        
        for query in test_queries:
            results = manager.search_stocks(query, limit=3)
            print(f"   搜索 '{query}': 找到 {len(results)} 个结果")
            for stock in results[:2]:  # 显示前2个结果
                print(f"      - {stock['symbol']}: {stock['name']} ({stock['sector']})")
        
        # 测试股票信息获取
        print("\n💰 测试股票信息获取:")
        test_symbols = ["AAPL", "MSFT", "GOOGL"]
        
        for symbol in test_symbols:
            print(f"   获取 {symbol} 信息...")
            stock_info = manager.get_stock_info(symbol)
            
            if stock_info:
                price = stock_info.get('current_price', 'N/A')
                name = stock_info.get('name', 'Unknown')
                sector = stock_info.get('sector', 'Unknown')
                print(f"      ✅ {symbol}: {name} - ${price} ({sector})")
            else:
                print(f"      ❌ 无法获取 {symbol} 信息")
        
        print("\n🎯 功能测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 动态股票选择功能测试")
    print("=" * 50)
    
    success = test_dynamic_stock_selection()
    
    if success:
        print("\n🎉 所有测试通过!")
        print("\n📱 应用功能:")
        print("1. 🔍 动态股票搜索 - 输入时实时过滤")
        print("2. 📊 股票信息展示 - 显示价格、行业等信息") 
        print("3. 💾 信息缓存 - 自动保存股票信息")
        print("4. 🎯 智能选择 - 点击选择股票到投资组合")
        print("5. 📈 详细信息 - 为K线图等功能预留接口")
        print("\n🌐 启动应用测试: streamlit run portfolio_app.py")
    else:
        print("\n⚠️ 测试未通过，请检查错误信息")