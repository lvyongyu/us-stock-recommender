"""
Input parser for multi-stock analysis

Supported input formats:
- Command line input (less than 5 stocks)
- File input (.txt, .csv formats)
- Stock symbol normalization and validation
"""

import os
import csv
import re
from typing import List, Set, Dict, Optional
from pathlib import Path


class InputParser:
    """Multi-stock input parser"""
    
    def __init__(self, lang_config=None):
        self.lang_config = lang_config
        self.supported_formats = {'.txt', '.csv'}
        self.max_command_line_stocks = 5  # Command line supports maximum 5 stocks
    
    def parse_input(self, symbols: Optional[str] = None, file_path: Optional[str] = None) -> Dict:
        """
        Parse stock input
        
        Args:
            symbols: Command line stock symbols string (comma separated)
            file_path: Stock list file path
            
        Returns:
            {
                'symbols': List[str],     # Stock symbol list
                'source': str,            # Input source: 'command' or 'file'
                'original_count': int,    # Original input count
                'valid_count': int,       # Valid stock count
                'errors': List[str]       # Error message list
            }
        """
        result = {
            'symbols': [],
            'source': '',
            'original_count': 0,
            'valid_count': 0,
            'errors': []
        }
        
        try:
            if symbols and file_path:
                error_msg = self.lang_config.get("cannot_use_both_input") if self.lang_config else "Cannot use both command line and file input"
                result['errors'].append(error_msg)
                return result
            
            if not symbols and not file_path:
                error_msg = self.lang_config.get("must_specify_input") if self.lang_config else "Must specify stock symbols or file path"
                result['errors'].append(error_msg)
                return result
            
            # Parse command line input
            if symbols:
                raw_symbols = self._parse_command_line_symbols(symbols)
                result['source'] = 'command'
                result['original_count'] = len(raw_symbols)
                
                # Check command line stock quantity limit
                if len(raw_symbols) > self.max_command_line_stocks:
                    if self.lang_config:
                        error_msg = self.lang_config.get("command_line_limit_exceeded").format(self.max_command_line_stocks)
                    else:
                        error_msg = f"Command line input exceeds {self.max_command_line_stocks} stocks, please use file input"
                    result['errors'].append(error_msg)
                    return result
                
                # Normalize stock symbols
                valid_symbols = self._normalize_symbols(raw_symbols)
                result['symbols'] = valid_symbols
                result['valid_count'] = len(valid_symbols)
            
            # Parse file input
            elif file_path:
                raw_symbols = self._parse_file_symbols(file_path)
                result['source'] = 'file'
                result['original_count'] = len(raw_symbols)
                
                # Normalize stock symbols
                valid_symbols = self._normalize_symbols(raw_symbols)
                result['symbols'] = valid_symbols
                result['valid_count'] = len(valid_symbols)
            
            # Check if there are valid stock symbols
            if result['valid_count'] == 0:
                error_msg = self.lang_config.get("no_valid_stock_symbols") if self.lang_config else "No valid stock symbols found"
                result['errors'].append(error_msg)
            
            return result
            
        except Exception as e:
            if self.lang_config:
                error_msg = self.lang_config.get("parsing_failed").format(str(e))
            else:
                error_msg = f"Input parsing failed: {str(e)}"
            result['errors'].append(error_msg)
            return result
    
    def _parse_command_line_symbols(self, symbols: str) -> List[str]:
        """Parse command line stock symbols"""
        if not symbols or not symbols.strip():
            return []
        
        # Split by comma and remove whitespace
        raw_symbols = [s.strip() for s in symbols.split(',')]
        return [s for s in raw_symbols if s]  # Filter empty strings
    
    def _parse_file_symbols(self, file_path: str) -> List[str]:
        """Parse stock symbols from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            if self.lang_config:
                error_msg = self.lang_config.get("file_not_found").format(file_path)
            else:
                error_msg = f"File does not exist: {file_path}"
            raise FileNotFoundError(error_msg)
        
        if file_path.suffix.lower() not in self.supported_formats:
            if self.lang_config:
                error_msg = self.lang_config.get("unsupported_file_format").format(file_path.suffix)
            else:
                error_msg = f"Unsupported file format: {file_path.suffix}"
            raise ValueError(error_msg)
        
        symbols = []
        
        try:
            if file_path.suffix.lower() == '.txt':
                symbols = self._parse_txt_file(file_path)
            elif file_path.suffix.lower() == '.csv':
                symbols = self._parse_csv_file(file_path)
        except Exception as e:
            if self.lang_config:
                error_msg = self.lang_config.get("file_parsing_failed").format(str(e))
            else:
                error_msg = f"Failed to parse file: {str(e)}"
            raise Exception(error_msg)
        
        return symbols
    
    def _parse_txt_file(self, file_path: Path) -> List[str]:
        """Parse .txt file"""
        symbols = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comment lines (starting with #)
                if not line or line.startswith('#'):
                    continue
                
                # Support multiple stock symbols per line (comma or space separated)
                if ',' in line:
                    symbols.extend([s.strip() for s in line.split(',') if s.strip()])
                else:
                    symbols.extend([s.strip() for s in line.split() if s.strip()])
        
        return symbols
    
    def _parse_csv_file(self, file_path: Path) -> List[str]:
        """Parse .csv file"""
        symbols = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Detect CSV format
            sample = f.read(1024)
            f.seek(0)
            
            # Use csv.Sniffer to detect dialect
            try:
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.reader(f, dialect)
            except csv.Error:
                # If detection fails, use default settings
                reader = csv.reader(f)
            
            for row_num, row in enumerate(reader, 1):
                if not row:  # Skip empty rows
                    continue
                
                # Assume first column is stock symbol
                symbol = str(row[0]).strip()
                
                # Skip header row (containing common header words)
                if row_num == 1 and symbol.lower() in ['symbol', 'stock', 'ticker', 'code', '股票代码', '代码']:
                    continue
                
                if symbol:
                    symbols.append(symbol)
        
        return symbols
    
    def _normalize_symbols(self, raw_symbols: List[str]) -> List[str]:
        """
        Normalize stock symbols
        - Convert to uppercase
        - Remove special characters
        - Basic format validation
        - Remove duplicates
        """
        normalized = []
        seen = set()
        
        for symbol in raw_symbols:
            if not symbol:
                continue
            
            # Convert to uppercase and remove leading/trailing whitespace
            clean_symbol = symbol.strip().upper()
            
            # Basic format validation (US stock symbols are usually 1-5 letters)
            if self._is_valid_symbol_format(clean_symbol):
                if clean_symbol not in seen:
                    normalized.append(clean_symbol)
                    seen.add(clean_symbol)
        
        return normalized
    
    def _is_valid_symbol_format(self, symbol: str) -> bool:
        """
        Validate stock symbol format
        US stock format: 1-5 letters, may include dots (e.g., BRK.A)
        """
        if not symbol:
            return False
        
        # Basic length check
        if len(symbol) < 1 or len(symbol) > 10:
            return False
        
        # Regular expression to validate US stock symbol format
        # Supports: AAPL, BRK.A, GOOGL, etc.
        pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
        
        return bool(re.match(pattern, symbol))
    
    def create_sample_files(self, base_path: str = ".") -> Dict[str, str]:
        """
        Create sample files for testing
        
        Returns:
            Dict[str, str]: Dictionary of file paths
        """
        base_path = Path(base_path)
        files_created = {}
        
        # Create sample .txt file
        txt_file = base_path / "sample_stocks.txt"
        txt_content = """# Sample stock list
# One or more stock symbols per line

AAPL
MSFT
GOOGL
TSLA
AMZN
NVDA
META
NFLX

# Can also use comma separation
JPM, BAC, WFC
ORCL CSCO IBM
"""
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        files_created['txt'] = str(txt_file)
        
        # Create sample .csv file
        csv_file = base_path / "sample_stocks.csv"
        csv_content = """Symbol,Company,Sector
AAPL,Apple Inc,Technology
MSFT,Microsoft Corporation,Technology
GOOGL,Alphabet Inc,Technology
TSLA,Tesla Inc,Consumer Discretionary
AMZN,Amazon.com Inc,Consumer Discretionary
NVDA,NVIDIA Corporation,Technology
META,Meta Platforms Inc,Technology
NFLX,Netflix Inc,Communication Services
JPM,JPMorgan Chase & Co,Financial Services
BAC,Bank of America Corp,Financial Services"""
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        files_created['csv'] = str(csv_file)
        
        return files_created


def test_input_parser():
    """Test input parser functionality"""
    parser = InputParser()
    
    print("🧪 Testing input parser...")
    
    # Test 1: Command line input
    print("\n1. Test command line input:")
    result = parser.parse_input(symbols="AAPL,MSFT,GOOGL,TSLA")
    print(f"   Input: 'AAPL,MSFT,GOOGL,TSLA'")
    print(f"   Result: {result['valid_count']} stocks - {result['symbols']}")
    
    # Test 2: Command line limit exceeded
    print("\n2. Test command line limit:")
    result = parser.parse_input(symbols="AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA")
    print(f"   Input: 6 stocks")
    print(f"   Errors: {result['errors']}")
    
    # Test 3: Create and parse sample files
    print("\n3. Test file input:")
    files = parser.create_sample_files()
    
    # Test TXT file
    result = parser.parse_input(file_path=files['txt'])
    print(f"   TXT file: {result['valid_count']} stocks")
    print(f"   First 5: {result['symbols'][:5]}")
    
    # Test CSV file  
    result = parser.parse_input(file_path=files['csv'])
    print(f"   CSV file: {result['valid_count']} stocks")
    print(f"   First 5: {result['symbols'][:5]}")
    
    print("\n✅ Input parser test completed!")


if __name__ == "__main__":
    test_input_parser()