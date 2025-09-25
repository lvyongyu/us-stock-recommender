"""
Portfolio Management System Exceptions

Custom exception classes for portfolio management operations.
Provides specific error types for better error handling and debugging.
"""


class PortfolioError(Exception):
    """Base exception class for all portfolio-related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class PortfolioNotFoundError(PortfolioError):
    """Raised when a requested portfolio cannot be found."""
    
    def __init__(self, portfolio_name: str):
        super().__init__(
            message=f"Portfolio '{portfolio_name}' not found",
            error_code="PORTFOLIO_NOT_FOUND"
        )
        self.portfolio_name = portfolio_name


class InvalidWeightError(PortfolioError):
    """Raised when portfolio weights are invalid."""
    
    def __init__(self, message: str, total_weight: float = None):
        super().__init__(message, "INVALID_WEIGHT")
        self.total_weight = total_weight


class DuplicatePortfolioError(PortfolioError):
    """Raised when attempting to create a portfolio with existing name."""
    
    def __init__(self, portfolio_name: str):
        super().__init__(
            message=f"Portfolio '{portfolio_name}' already exists",
            error_code="DUPLICATE_PORTFOLIO"
        )
        self.portfolio_name = portfolio_name


class FileOperationError(PortfolioError):
    """Raised when file operations fail."""
    
    def __init__(self, operation: str, file_path: str, original_error: Exception = None):
        message = f"Failed to {operation} file '{file_path}'"
        if original_error:
            message += f": {str(original_error)}"
        
        super().__init__(message, "FILE_OPERATION_ERROR")
        self.operation = operation
        self.file_path = file_path
        self.original_error = original_error


class ValidationError(PortfolioError):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: any, message: str = None):
        if not message:
            message = f"Invalid value for field '{field}': {value}"
        
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class InsufficientDataError(PortfolioError):
    """Raised when insufficient data for analysis."""
    
    def __init__(self, data_type: str, minimum_required: int = None):
        message = f"Insufficient {data_type} for analysis"
        if minimum_required:
            message += f" (minimum required: {minimum_required})"
        
        super().__init__(message, "INSUFFICIENT_DATA")
        self.data_type = data_type
        self.minimum_required = minimum_required


class AnalysisError(PortfolioError):
    """Raised when portfolio analysis fails."""
    
    def __init__(self, analysis_type: str, reason: str = None):
        message = f"Failed to perform {analysis_type} analysis"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, "ANALYSIS_ERROR")
        self.analysis_type = analysis_type
        self.reason = reason