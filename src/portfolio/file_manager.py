"""
Portfolio File Management System

Handles file-based persistence operations for portfolios including:
- JSON format save/load operations
- Backup and recovery functionality
- File validation and error handling
- Directory management

Supports multiple portfolio storage and retrieval with data integrity checks.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from .models import Portfolio
from .exceptions import FileOperationError, ValidationError


class FileManager:
    """Manages file operations for portfolio persistence."""
    
    def __init__(self, base_path: str = None, backup_enabled: bool = True, max_backups: int = 10):
        """
        Initialize file manager with configuration.
        
        Args:
            base_path: Base directory for portfolio storage
            backup_enabled: Whether to create automatic backups
            max_backups: Maximum number of backup files to keep
        """
        self.base_path = Path(base_path or self._get_default_path())
        self.backup_enabled = backup_enabled
        self.max_backups = max_backups
        
        # Ensure directories exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        if self.backup_enabled:
            self.backup_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def backup_path(self) -> Path:
        """Get backup directory path."""
        return self.base_path / "backups"
    
    def _get_default_path(self) -> str:
        """Get default storage path based on system."""
        home = Path.home()
        return str(home / ".stock_recommender" / "portfolios")
    
    def _get_portfolio_file_path(self, portfolio_name: str) -> Path:
        """Get full file path for a portfolio."""
        filename = self._sanitize_filename(portfolio_name) + ".json"
        return self.base_path / filename
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize portfolio name for use as filename."""
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        sanitized = ''.join('_' if c in invalid_chars else c for c in name)
        # Limit length and remove leading/trailing spaces
        return sanitized[:100].strip()
    
    def _create_backup(self, portfolio_name: str) -> Optional[str]:
        """Create backup of existing portfolio file."""
        if not self.backup_enabled:
            return None
        
        source_file = self._get_portfolio_file_path(portfolio_name)
        if not source_file.exists():
            return None
        
        try:
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self._sanitize_filename(portfolio_name)}_{timestamp}.json"
            backup_file = self.backup_path / backup_filename
            
            shutil.copy2(source_file, backup_file)
            
            # Clean up old backups
            self._cleanup_old_backups(portfolio_name)
            
            return str(backup_file)
            
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Warning: Failed to create backup for {portfolio_name}: {e}")
            return None
    
    def _cleanup_old_backups(self, portfolio_name: str):
        """Remove old backup files beyond max_backups limit."""
        if not self.backup_enabled or self.max_backups <= 0:
            return
        
        try:
            sanitized_name = self._sanitize_filename(portfolio_name)
            pattern = f"{sanitized_name}_*.json"
            
            backup_files = list(self.backup_path.glob(pattern))
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Remove old backups beyond the limit
            for old_backup in backup_files[self.max_backups:]:
                old_backup.unlink()
                
        except Exception as e:
            print(f"Warning: Failed to cleanup old backups: {e}")
    
    def save_portfolio(self, portfolio: Portfolio, file_path: Optional[str] = None) -> str:
        """
        Save portfolio to JSON file.
        
        Args:
            portfolio: Portfolio instance to save
            file_path: Optional custom file path (defaults to standard path)
            
        Returns:
            str: Path to saved file
            
        Raises:
            FileOperationError: If save operation fails
        """
        try:
            if file_path:
                target_file = Path(file_path)
                target_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                target_file = self._get_portfolio_file_path(portfolio.name)
                
                # Create backup if file exists
                if target_file.exists():
                    self._create_backup(portfolio.name)
            
            # Convert portfolio to dictionary
            portfolio_data = portfolio.to_dict()
            
            # Add metadata
            portfolio_data['_metadata'] = {
                'version': '1.0',
                'saved_time': datetime.now().isoformat(),
                'file_format': 'json'
            }
            
            # Write to file
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(portfolio_data, f, indent=2, ensure_ascii=False)
            
            return str(target_file)
            
        except Exception as e:
            raise FileOperationError("save", str(target_file), e)
    
    def load_portfolio(self, file_path: str) -> Portfolio:
        """
        Load portfolio from JSON file.
        
        Args:
            file_path: Path to portfolio file
            
        Returns:
            Portfolio: Loaded portfolio instance
            
        Raises:
            FileOperationError: If load operation fails
            ValidationError: If data validation fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileOperationError("load", str(file_path), 
                                    FileNotFoundError(f"File not found: {file_path}"))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate file format
            self._validate_file_data(data)
            
            # Remove metadata before creating portfolio
            data.pop('_metadata', None)
            
            # Create portfolio from data
            portfolio = Portfolio.from_dict(data)
            
            return portfolio
            
        except json.JSONDecodeError as e:
            raise FileOperationError("load", str(file_path), e)
        except Exception as e:
            raise FileOperationError("load", str(file_path), e)
    
    def _validate_file_data(self, data: Dict[str, Any]):
        """Validate loaded file data structure."""
        required_fields = ['id', 'name', 'created_time']
        
        for field in required_fields:
            if field not in data:
                raise ValidationError(field, None, f"Required field '{field}' missing from file")
        
        # Check file version compatibility
        metadata = data.get('_metadata', {})
        file_version = metadata.get('version', '1.0')
        
        if file_version != '1.0':
            print(f"Warning: File version {file_version} may not be fully compatible")
    
    def delete_portfolio_file(self, portfolio_name: str) -> bool:
        """
        Delete portfolio file.
        
        Args:
            portfolio_name: Name of portfolio to delete
            
        Returns:
            bool: True if file was deleted, False if file didn't exist
            
        Raises:
            FileOperationError: If deletion fails
        """
        file_path = self._get_portfolio_file_path(portfolio_name)
        
        if not file_path.exists():
            return False
        
        try:
            # Create backup before deletion
            backup_file = self._create_backup(portfolio_name)
            if backup_file:
                print(f"Portfolio backed up to: {backup_file}")
            
            file_path.unlink()
            return True
            
        except Exception as e:
            raise FileOperationError("delete", str(file_path), e)
    
    def list_portfolio_files(self) -> List[str]:
        """
        List all portfolio files in the base directory.
        
        Returns:
            List[str]: List of portfolio file names (without extension)
        """
        try:
            portfolio_files = []
            
            for file_path in self.base_path.glob("*.json"):
                # Skip backup files and metadata files
                if not file_path.name.startswith('.') and '_' not in file_path.stem:
                    portfolio_files.append(file_path.stem)
            
            return sorted(portfolio_files)
            
        except Exception as e:
            print(f"Warning: Error listing portfolio files: {e}")
            return []
    
    def export_to_csv(self, portfolio: Portfolio, file_path: str) -> str:
        """
        Export portfolio holdings to CSV format.
        
        Args:
            portfolio: Portfolio to export
            file_path: Target CSV file path
            
        Returns:
            str: Path to exported file
        """
        try:
            import csv
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['symbol', 'weight', 'target_weight', 'recommendation', 
                             'confidence', 'notes', 'last_updated']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for holding in portfolio.holdings:
                    writer.writerow({
                        'symbol': holding.symbol,
                        'weight': f"{holding.weight:.4f}",
                        'target_weight': f"{holding.target_weight:.4f}" if holding.target_weight else "",
                        'recommendation': holding.recommendation or "",
                        'confidence': f"{holding.confidence:.4f}" if holding.confidence else "",
                        'notes': holding.notes,
                        'last_updated': holding.last_updated.isoformat()
                    })
            
            return str(file_path)
            
        except Exception as e:
            raise FileOperationError("export_csv", str(file_path), e)
    
    def import_stocks_from_csv(self, file_path: str) -> List[tuple[str, float]]:
        """
        Import stock symbols and weights from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List[tuple[str, float]]: List of (symbol, weight) tuples
            
        Raises:
            FileOperationError: If import fails
        """
        try:
            import csv
            
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileOperationError("import_csv", str(file_path), 
                                        FileNotFoundError("CSV file not found"))
            
            stocks = []
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Try to detect if first row is header
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                has_header = sniffer.has_header(sample)
                
                reader = csv.reader(csvfile)
                
                if has_header:
                    next(reader)  # Skip header row
                
                for row in reader:
                    if len(row) >= 2:
                        symbol = row[0].strip().upper()
                        try:
                            weight = float(row[1])
                            if symbol and 0.0 <= weight <= 1.0:
                                stocks.append((symbol, weight))
                        except ValueError:
                            continue  # Skip invalid weight values
            
            return stocks
            
        except Exception as e:
            raise FileOperationError("import_csv", str(file_path), e)
    
    def get_file_info(self, portfolio_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a portfolio file.
        
        Args:
            portfolio_name: Name of portfolio
            
        Returns:
            Dict with file information or None if file doesn't exist
        """
        file_path = self._get_portfolio_file_path(portfolio_name)
        
        if not file_path.exists():
            return None
        
        try:
            stat = file_path.stat()
            
            return {
                'file_path': str(file_path),
                'size_bytes': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            print(f"Warning: Error getting file info for {portfolio_name}: {e}")
            return None
    
    def restore_from_backup(self, backup_file: str) -> Portfolio:
        """
        Restore portfolio from backup file.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            Portfolio: Restored portfolio instance
        """
        return self.load_portfolio(backup_file)
    
    def list_backups(self, portfolio_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available backup files.
        
        Args:
            portfolio_name: Optional filter by portfolio name
            
        Returns:
            List of backup file information
        """
        if not self.backup_enabled or not self.backup_path.exists():
            return []
        
        try:
            backups = []
            pattern = "*.json"
            
            if portfolio_name:
                sanitized_name = self._sanitize_filename(portfolio_name)
                pattern = f"{sanitized_name}_*.json"
            
            for backup_file in self.backup_path.glob(pattern):
                stat = backup_file.stat()
                backups.append({
                    'file_path': str(backup_file),
                    'portfolio_name': backup_file.name.split('_')[0],
                    'backup_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size_bytes': stat.st_size
                })
            
            # Sort by backup time, newest first
            backups.sort(key=lambda x: x['backup_time'], reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"Warning: Error listing backups: {e}")
            return []