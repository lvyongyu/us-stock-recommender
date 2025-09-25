"""
Tests for multi-stock input parser functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.batch.input_parser import InputParser


class TestInputParser(unittest.TestCase):
    """Test input parser"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = InputParser()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_command_line_input_valid(self):
        """Test valid command line input"""
        result = self.parser.parse_input(symbols="AAPL,MSFT,GOOGL")
        
        self.assertEqual(result['source'], 'command')
        self.assertEqual(result['valid_count'], 3)
        self.assertIn('AAPL', result['symbols'])
        self.assertIn('MSFT', result['symbols'])
        self.assertIn('GOOGL', result['symbols'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_command_line_input_too_many_stocks(self):
        """Test command line input with too many stocks"""
        symbols = "AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA"  # 6 stocks
        result = self.parser.parse_input(symbols=symbols)
        
        self.assertEqual(len(result['errors']), 1)
        self.assertIn("Command line input exceeds 5 stocks", result['errors'][0])
    
    def test_command_line_input_normalization(self):
        """Test stock symbol normalization"""
        result = self.parser.parse_input(symbols="aapl, MSFT , googl")
        
        self.assertEqual(result['valid_count'], 3)
        self.assertIn('AAPL', result['symbols'])
        self.assertIn('MSFT', result['symbols'])
        self.assertIn('GOOGL', result['symbols'])
    
    def test_command_line_input_deduplication(self):
        """Test stock symbol deduplication"""
        result = self.parser.parse_input(symbols="AAPL,MSFT,AAPL,GOOGL")
        
        self.assertEqual(result['valid_count'], 3)
        self.assertEqual(result['symbols'].count('AAPL'), 1)
    
    def test_txt_file_input(self):
        """Test .txt file input"""
        # Create temporary txt file
        txt_file = Path(self.temp_dir) / "test_stocks.txt"
        with open(txt_file, 'w') as f:
            f.write("# Test stock list\nAAPL\nMSFT\nGOOGL\n\n# Comment line\nTSLA\n")
        
        result = self.parser.parse_input(file_path=str(txt_file))
        
        self.assertEqual(result['source'], 'file')
        self.assertEqual(result['valid_count'], 4)
        self.assertIn('AAPL', result['symbols'])
        self.assertIn('TSLA', result['symbols'])
    
    def test_csv_file_input(self):
        """Test .csv file input"""
        # Create temporary csv file
        csv_file = Path(self.temp_dir) / "test_stocks.csv"
        with open(csv_file, 'w') as f:
            f.write("Symbol,Company\nAAPL,Apple Inc\nMSFT,Microsoft\nGOOGL,Alphabet\n")
        
        result = self.parser.parse_input(file_path=str(csv_file))
        
        self.assertEqual(result['source'], 'file')
        self.assertEqual(result['valid_count'], 3)
        self.assertIn('AAPL', result['symbols'])
        self.assertIn('GOOGL', result['symbols'])
    
    def test_file_not_found(self):
        """Test file not found scenario"""
        result = self.parser.parse_input(file_path="/nonexistent/file.txt")
        
        self.assertEqual(len(result['errors']), 1)
        self.assertIn("File does not exist", result['errors'][0])
    
    def test_unsupported_file_format(self):
        """Test unsupported file format"""
        # Create .json file (unsupported format)
        json_file = Path(self.temp_dir) / "test_stocks.json"
        with open(json_file, 'w') as f:
            f.write('{"stocks": ["AAPL", "MSFT"]}')
        
        result = self.parser.parse_input(file_path=str(json_file))
        
        self.assertEqual(len(result['errors']), 1)
        self.assertIn("Unsupported file format", result['errors'][0])
    
    def test_both_symbols_and_file(self):
        """Test providing both command line and file input"""
        result = self.parser.parse_input(symbols="AAPL", file_path="test.txt")
        
        self.assertEqual(len(result['errors']), 1)
        self.assertIn("Cannot use both command line and file input", result['errors'][0])
    
    def test_no_input(self):
        """Test when no input is provided"""
        result = self.parser.parse_input()
        
        self.assertEqual(len(result['errors']), 1)
        self.assertIn("Must specify stock symbols or file path", result['errors'][0])
    
    def test_symbol_format_validation(self):
        """Test stock symbol format validation"""
        # Test valid formats
        self.assertTrue(self.parser._is_valid_symbol_format("AAPL"))
        self.assertTrue(self.parser._is_valid_symbol_format("BRK.A"))
        self.assertTrue(self.parser._is_valid_symbol_format("GOOGL"))
        
        # Test invalid formats
        self.assertFalse(self.parser._is_valid_symbol_format(""))
        self.assertFalse(self.parser._is_valid_symbol_format("123"))
        self.assertFalse(self.parser._is_valid_symbol_format("TOOLONG"))
        self.assertFalse(self.parser._is_valid_symbol_format("A@PPL"))
    
    def test_normalize_symbols(self):
        """Test stock symbol normalization functionality"""
        input_symbols = ["aapl", " MSFT ", "googl", "", "INVALID@", "BRK.A"]
        result = self.parser._normalize_symbols(input_symbols)
        
        expected = ["AAPL", "MSFT", "GOOGL", "BRK.A"]
        self.assertEqual(result, expected)


class TestInputParserIntegration(unittest.TestCase):
    """Input parser integration tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = InputParser()
    
    def test_create_sample_files(self):
        """Test sample file creation functionality"""
        files = self.parser.create_sample_files()
        
        self.assertIn('txt', files)
        self.assertIn('csv', files)
        
        # Verify files exist
        self.assertTrue(os.path.exists(files['txt']))
        self.assertTrue(os.path.exists(files['csv']))
        
        # Test parsing created files
        txt_result = self.parser.parse_input(file_path=files['txt'])
        csv_result = self.parser.parse_input(file_path=files['csv'])
        
        self.assertGreater(txt_result['valid_count'], 0)
        self.assertGreater(csv_result['valid_count'], 0)
        
        # Clean up
        os.remove(files['txt'])
        os.remove(files['csv'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)