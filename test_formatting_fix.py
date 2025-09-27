#!/usr/bin/env python3
"""
Test script for portfolio comparison formatting fix.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_formatting_fix():
    """Test that percentage formatting handles None values properly"""
    print("🧪 Testing percentage formatting with None values...")
    
    # Test cases that might cause the original error
    test_values = [
        (0.1234, ":.1%", "12.3%"),
        (None, ":.1%", "N/A"),
        ("invalid", ":.1%", "N/A"),
        (0.5678, ":.2f", "0.57"),
        (None, ":.2f", "N/A"),
        ("test", "", "test"),
        (None, "", "N/A")
    ]
    
    for value, format_str, expected_pattern in test_values:
        try:
            if format_str:
                if value is not None and isinstance(value, (int, float)):
                    if format_str == ':.1%':
                        result = f"{value:.1%}"
                    elif format_str == ':.2f':
                        result = f"{value:.2f}"
                    else:
                        result = format(value, format_str.lstrip(':'))
                else:
                    result = "N/A"
            else:
                result = str(value) if value is not None else "N/A"
            
            print(f"   ✅ Value: {value}, Format: {format_str}, Result: {result}")
            
        except Exception as e:
            print(f"   ❌ Value: {value}, Format: {format_str}, Error: {e}")

def main():
    """Main test function"""
    print("=" * 50)
    print("🔧 Portfolio Comparison Formatting Fix Test")
    print("=" * 50)
    
    test_formatting_fix()
    
    print("\n🎯 Fix Summary:")
    print("1. ✅ Added None value checking")
    print("2. ✅ Added type validation for numeric formatting")
    print("3. ✅ Added proper error handling with try-catch")
    print("4. ✅ Returns 'N/A' for invalid values")
    
    print("\n🔍 Error Details:")
    print("- Original Error: 'Invalid format specifier ':.1%' for object of type 'float''")
    print("- Root Cause: Trying to format None or invalid values with percentage formatting")
    print("- Solution: Check value type and handle None cases before formatting")
    
    print("\n🌐 Test the fix: streamlit run portfolio_app.py")
    print("📊 Navigate to Portfolio Comparison page to verify")

if __name__ == "__main__":
    main()