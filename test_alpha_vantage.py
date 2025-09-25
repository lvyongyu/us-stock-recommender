#!/usr/bin/env python3
"""
Alpha Vantage API Test Script
测试Alpha Vantage API连接和基本功能

Usage: python test_alpha_vantage.py
"""

import os
import sys
from dotenv import load_dotenv
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import time

def main():
    print("🚀 Alpha Vantage API 测试开始...")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        print("❌ 错误: 未找到 ALPHA_VANTAGE_API_KEY")
        print("请检查 .env 文件是否存在且包含正确的API密钥")
        return False
    
    print(f"✅ API密钥已加载: {api_key[:8]}...{api_key[-4:]}")
    
    # 初始化客户端
    ts = TimeSeries(key=api_key, output_format='pandas')
    ti = TechIndicators(key=api_key, output_format='pandas')
    
    test_symbol = "AAPL"  # 使用苹果股票作为测试
    
    try:
        print(f"\n📊 测试1: 获取 {test_symbol} 实时数据...")
        
        # 获取实时数据 (每日数据，因为intraday需要更多配置)
        data, meta_data = ts.get_daily(symbol=test_symbol, outputsize='compact')
        
        if not data.empty:
            latest_data = data.iloc[0]
            latest_date = data.index[0]
            
            print(f"✅ 成功获取数据!")
            print(f"   最新日期: {latest_date}")
            print(f"   收盘价: ${latest_data['4. close']:.2f}")
            print(f"   成交量: {latest_data['5. volume']:,}")
            print(f"   数据行数: {len(data)}")
        else:
            print("❌ 未获取到数据")
            return False
            
        # 等待1秒避免API限制
        time.sleep(1)
        
        print(f"\n📈 测试2: 获取 {test_symbol} 技术指标 (RSI)...")
        
        # 获取RSI指标
        rsi_data, rsi_meta = ti.get_rsi(symbol=test_symbol, interval='daily')
        
        if not rsi_data.empty:
            latest_rsi = rsi_data.iloc[0]['RSI']
            print(f"✅ 成功获取RSI数据!")
            print(f"   最新RSI: {latest_rsi:.2f}")
            print(f"   RSI数据行数: {len(rsi_data)}")
        else:
            print("❌ 未获取到RSI数据")
            return False
            
        time.sleep(1)
        
        print(f"\n💹 测试3: 获取 {test_symbol} 分钟级数据...")
        
        # 获取分钟级数据
        intraday_data, intraday_meta = ts.get_intraday(symbol=test_symbol, interval='5min', outputsize='compact')
        
        if not intraday_data.empty:
            latest_minute_data = intraday_data.iloc[0]
            latest_minute_time = intraday_data.index[0]
            
            print(f"✅ 成功获取分钟级数据!")
            print(f"   最新时间: {latest_minute_time}")
            print(f"   最新价格: ${latest_minute_data['4. close']:.2f}")
            print(f"   分钟级数据行数: {len(intraday_data)}")
        else:
            print("❌ 未获取到分钟级数据")
            return False
        
        print(f"\n🎯 API测试总结:")
        print(f"   ✅ 日线数据: 正常")
        print(f"   ✅ 技术指标: 正常") 
        print(f"   ✅ 分钟级数据: 正常")
        print(f"   📊 建议单只股票完整分析消耗API调用: ~20-25次")
        print(f"   💡 免费额度500次/天，建议分析15-20只股票")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Alpha Vantage API测试成功! 可以开始集成到项目中。")
    else:
        print("\n💥 Alpha Vantage API测试失败，请检查配置。")
        sys.exit(1)