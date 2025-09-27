#!/usr/bin/env python3
"""
Test script for the updated dynamic stock selection with empty default results.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.utils.stock_info_manager import StockInfoManager
    from src.utils.stock_selector import create_dynamic_stock_selector
    print("✅ Modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_empty_search():
    """Test that empty search returns no results"""
    print("\n📋 Testing empty search behavior:")
    
    manager = StockInfoManager()
    
    # Test empty string search
    empty_results = manager.search_stocks("", limit=10)
    print(f"   Empty string search: {len(empty_results)} results")
    
    # Test with whitespace only
    whitespace_results = manager.search_stocks("   ", limit=10)
    print(f"   Whitespace only search: {len(whitespace_results)} results")
    
    # Test normal search
    apple_results = manager.search_stocks("AAPL", limit=10)
    print(f"   'AAPL' search: {len(apple_results)} results")
    
    if len(empty_results) == 0 and len(whitespace_results) == 0 and len(apple_results) > 0:
        print("   ✅ Empty search behavior works correctly!")
    else:
        print("   ❌ Empty search behavior needs adjustment")

def main():
    """Main test function"""
    print("=" * 50)
    print("🚀 Updated Dynamic Stock Selection Test")
    print("=" * 50)
    
    test_empty_search()
    
    print("\n🎯 New Features:")
    print("1. 🔍 No stocks displayed by default")
    print("2. 💡 Helpful tip shown when search is empty") 
    print("3. 📈 Results only appear after user input")
    print("4. 🎯 Better user experience with guided interaction")
    
    print("\n🌐 Test the app: streamlit run portfolio_app.py")
    print("📍 App is running at: http://localhost:8502")

if __name__ == "__main__":
    main()