"""
End-to-end integration tests for multi-stock functionality
"""

import unittest
import tempfile
import os
import subprocess
import sys
from pathlib import Path


class TestMultiStockIntegration(unittest.TestCase):
    """Multi-stock functionality integration tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.python_path = sys.executable
        self.script_path = Path(__file__).parent.parent / "stock_recommender.py"
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_help_command(self):
        """Test help command displays multi-stock options"""
        result = subprocess.run([
            self.python_path, str(self.script_path), "--help"
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("--multi", result.stdout)
        self.assertIn("--file", result.stdout)
        self.assertIn("多股票模式", result.stdout)
    
    def test_single_stock_mode_still_works(self):
        """Test single stock mode still works properly"""
        result = subprocess.run([
            self.python_path, str(self.script_path), "AAPL", "--strategy=technical"
        ], capture_output=True, text=True, timeout=30)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("AAPL", result.stdout)
        self.assertIn("INVESTMENT RECOMMENDATION", result.stdout)
    
    def test_multi_stock_command_line_mode(self):
        """Test multi-stock command line mode"""
        result = subprocess.run([
            self.python_path, str(self.script_path), "--multi", "AAPL,MSFT,GOOGL"
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Successfully parsed 3/3 stocks", result.stdout)
        self.assertIn("Number of stocks: 3", result.stdout)
    
    def test_multi_stock_file_mode(self):
        """Test multi-stock file mode"""
        # Create test file
        test_file = Path(self.temp_dir) / "test_stocks.txt"
        with open(test_file, 'w') as f:
            f.write("AAPL\nMSFT\nGOOGL\nTSLA\n")
        
        result = subprocess.run([
            self.python_path, str(self.script_path), "--multi", "--file", str(test_file)
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Successfully parsed 4/4 stocks", result.stdout)
    
    def test_command_line_limit_enforcement(self):
        """Test command line stock quantity limit enforcement"""
        result = subprocess.run([
            self.python_path, str(self.script_path), "--multi", 
            "AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA"  # 6 stocks
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Command line input exceeds 5 stocks", result.stdout)
    
    def test_invalid_file_handling(self):
        """Test invalid file handling"""
        result = subprocess.run([
            self.python_path, str(self.script_path), "--multi", "--file", "nonexistent.txt"
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("File does not exist", result.stdout)
    
    def test_mutually_exclusive_arguments(self):
        """Test mutually exclusive arguments validation"""
        # Test providing both single stock and multi-stock arguments
        result = subprocess.run([
            self.python_path, str(self.script_path), "AAPL", "--multi", "MSFT"
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 2)  # argparse error
        self.assertIn("Cannot use single stock argument with multi-stock mode", result.stderr)
    
    def test_no_arguments_error(self):
        """Test error handling when no arguments provided"""
        result = subprocess.run([
            self.python_path, str(self.script_path)
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 2)  # argparse error
        self.assertIn("Must provide stock symbol or use multi-stock mode", result.stderr)
    
    def test_csv_file_input(self):
        """Test CSV file input"""
        # Create test CSV file
        csv_file = Path(self.temp_dir) / "test_stocks.csv"
        with open(csv_file, 'w') as f:
            f.write("Symbol,Company\nAAPL,Apple\nMSFT,Microsoft\nGOOGL,Alphabet\n")
        
        result = subprocess.run([
            self.python_path, str(self.script_path), "--multi", "--file", str(csv_file)
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Successfully parsed 3/3 stocks", result.stdout)
    
    def test_invalid_symbols_filtering(self):
        """Test invalid stock symbol filtering"""
        result = subprocess.run([
            self.python_path, str(self.script_path), "--multi", "AAPL,INVALID123,MSFT,@#$"
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Successfully parsed 2/4 stocks", result.stdout)  # Only AAPL and MSFT are valid
    
    def test_language_support_with_multi_stock(self):
        """Test language support with multi-stock mode"""
        result = subprocess.run([
            self.python_path, str(self.script_path), "--multi", "AAPL,MSFT", "--lang", "zh"
        ], capture_output=True, text=True, timeout=15)
        
        self.assertEqual(result.returncode, 0)
        # Check Chinese output
        # Note: Multi-stock functionality is still under development, mainly testing parsing section
        self.assertIn("成功解析", result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)