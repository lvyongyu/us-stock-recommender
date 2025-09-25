"""
Concurrent manager for multi-stock analysis

Implements thread pool management, API rate limiting, error handling, and resource control
"""

import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import List, Dict, Callable, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import queue
import logging


@dataclass
class ConcurrentConfig:
    """Concurrent configuration"""
    max_workers: int = 8           # Maximum number of worker threads
    api_rate_limit: float = 0.2    # API call interval (seconds) - yfinance limit
    batch_size: int = 10           # Batch processing size
    timeout_per_task: int = 30     # Single task timeout (seconds)
    max_retries: int = 3           # Maximum retry attempts
    retry_delay: float = 1.0       # Retry delay (seconds)


class APIRateLimiter:
    """API rate limiter"""
    
    def __init__(self, calls_per_second: float):
        self.min_interval = 1.0 / calls_per_second if calls_per_second > 0 else 0
        self.last_call_time = 0
        self._lock = threading.Lock()
    
    def acquire(self):
        """Acquire API call permission"""
        with self._lock:
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            
            if time_since_last_call < self.min_interval:
                sleep_time = self.min_interval - time_since_last_call
                time.sleep(sleep_time)
            
            self.last_call_time = time.time()


@dataclass
class TaskResult:
    """Task result"""
    symbol: str
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    attempts: int = 1
    duration: Optional[timedelta] = None


class ConcurrentManager:
    """Concurrent manager"""
    
    def __init__(self, config: Optional[ConcurrentConfig] = None, lang_config=None):
        self.config = config or ConcurrentConfig()
        self.lang_config = lang_config
        
        # Initialize components
        self.rate_limiter = APIRateLimiter(1.0 / self.config.api_rate_limit)
        self.executor = None
        self._running_tasks: Set[str] = set()
        self._lock = threading.Lock()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        """Enter context manager"""
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
    
    def execute_concurrent(
        self, 
        symbols: List[str], 
        task_func: Callable[[str], Dict],
        progress_callback: Optional[Callable[[str, str], None]] = None
    ) -> List[TaskResult]:
        """
        Execute tasks concurrently
        
        Args:
            symbols: List of stock symbols
            task_func: Single stock analysis function
            progress_callback: Progress callback function(symbol, status)
            
        Returns:
            List[TaskResult]: List of task results
        """
        if not self.executor:
            if self.lang_config:
                error_msg = self.lang_config.get("concurrent_manager_context_required")
            else:
                error_msg = "ConcurrentManager must be used within a 'with' statement"
            raise RuntimeError(error_msg)
        
        results = []
        future_to_symbol = {}
        
        # Submit all tasks
        for symbol in symbols:
            future = self.executor.submit(
                self._execute_task_with_retry,
                symbol,
                task_func,
                progress_callback
            )
            future_to_symbol[future] = symbol
        
        # Collect results
        for future in as_completed(future_to_symbol, timeout=len(symbols) * self.config.timeout_per_task):
            symbol = future_to_symbol[future]
            
            try:
                result = future.result()
                results.append(result)
                
                if progress_callback:
                    status = "completed" if result.success else "failed"
                    progress_callback(symbol, status)
                    
            except Exception as e:
                # Create failure result
                if self.lang_config:
                    error_msg = self.lang_config.get("task_execution_exception").format(str(e))
                else:
                    error_msg = f"Task execution exception: {str(e)}"
                error_result = TaskResult(
                    symbol=symbol,
                    success=False,
                    error=error_msg,
                    attempts=self.config.max_retries
                )
                results.append(error_result)
                
                if progress_callback:
                    progress_callback(symbol, "failed")
        
        return results
    
    def execute_batched(
        self,
        symbols: List[str],
        task_func: Callable[[str], Dict],
        progress_callback: Optional[Callable[[str, str], None]] = None
    ) -> List[TaskResult]:
        """
        Execute tasks in batches with concurrency
        
        Args:
            symbols: List of stock symbols
            task_func: Single stock analysis function
            progress_callback: Progress callback function
            
        Returns:
            List[TaskResult]: List of task results
        """
        all_results = []
        batch_size = self.config.batch_size
        
        # Process in batches
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            
            print(f"📦 Processing batch {i//batch_size + 1}/{(len(symbols) + batch_size - 1)//batch_size}: "
                  f"{len(batch_symbols)} stocks")
            
            # Execute current batch
            batch_results = self.execute_concurrent(batch_symbols, task_func, progress_callback)
            all_results.extend(batch_results)
            
            # Rest between batches to avoid API overload
            if i + batch_size < len(symbols):
                time.sleep(0.5)
        
        return all_results
    
    def _execute_task_with_retry(
        self,
        symbol: str,
        task_func: Callable[[str], Dict],
        progress_callback: Optional[Callable[[str, str], None]]
    ) -> TaskResult:
        """Execute task with retry logic"""
        start_time = datetime.now()
        
        # Mark task as started
        with self._lock:
            self._running_tasks.add(symbol)
        
        if progress_callback:
            progress_callback(symbol, "running")
        
        # Execute retry logic
        last_error = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                # Apply API rate limiting
                self.rate_limiter.acquire()
                
                # Execute task
                result = task_func(symbol)
                
                # Task successful
                duration = datetime.now() - start_time
                
                with self._lock:
                    self._running_tasks.discard(symbol)
                
                return TaskResult(
                    symbol=symbol,
                    success=True,
                    result=result,
                    attempts=attempt,
                    duration=duration
                )
                
            except Exception as e:
                last_error = str(e)
                
                if attempt < self.config.max_retries:
                    # Wait before retry
                    time.sleep(self.config.retry_delay * attempt)
                    continue
                else:
                    # All retries failed
                    break
        
        # Task ultimately failed
        duration = datetime.now() - start_time
        
        with self._lock:
            self._running_tasks.discard(symbol)
        
        return TaskResult(
            symbol=symbol,
            success=False,
            error=last_error or "Unknown error",
            attempts=self.config.max_retries,
            duration=duration
        )
    
    def get_running_tasks(self) -> Set[str]:
        """Get currently running tasks"""
        with self._lock:
            return self._running_tasks.copy()
    
    def is_running(self) -> bool:
        """Check if any tasks are running"""
        with self._lock:
            return len(self._running_tasks) > 0


def create_optimized_config(stock_count: int) -> ConcurrentConfig:
    """
    Create optimized concurrent configuration based on stock count
    
    Args:
        stock_count: Number of stocks
        
    Returns:
        ConcurrentConfig: Optimized configuration
    """
    if stock_count <= 5:
        # Small scale: fast processing
        return ConcurrentConfig(
            max_workers=3,
            api_rate_limit=0.1,  # Faster API calls
            batch_size=5,
            timeout_per_task=20,
            max_retries=2
        )
    elif stock_count <= 20:
        # Medium scale: balance performance and stability
        return ConcurrentConfig(
            max_workers=6,
            api_rate_limit=0.15,
            batch_size=10,
            timeout_per_task=25,
            max_retries=3
        )
    else:
        # Large scale: focus on stability
        return ConcurrentConfig(
            max_workers=8,
            api_rate_limit=0.2,  # More conservative API calls
            batch_size=15,
            timeout_per_task=30,
            max_retries=3
        )


def test_concurrent_manager():
    """Test concurrent manager"""
    print("🧪 Testing concurrent manager...")
    
    # Mock stock analysis function
    def mock_analyze_stock(symbol: str) -> Dict:
        """Mock stock analysis"""
        import random
        
        # Randomly simulate analysis time
        analysis_time = random.uniform(0.5, 2.0)
        time.sleep(analysis_time)
        
        # 10% failure probability
        if random.random() < 0.1:
            raise Exception(f"Mock API error - {symbol}")
        
        return {
            "symbol": symbol,
            "recommendation": random.choice(["Buy", "Hold", "Sell"]),
            "score": random.randint(30, 90),
            "analysis_time": analysis_time
        }
    
    # Test stock list
    test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
    
    # Create optimized configuration
    config = create_optimized_config(len(test_symbols))
    print(f"📋 Config: {config.max_workers} threads, {config.api_rate_limit}s interval, {config.batch_size} batch size")
    
    # Progress callback
    def progress_callback(symbol: str, status: str):
        status_emoji = {
            "running": "🔄",
            "completed": "✅", 
            "failed": "❌"
        }
        print(f"{status_emoji.get(status, '❓')} {symbol}: {status}")
    
    # Execute concurrent analysis
    start_time = time.time()
    
    with ConcurrentManager(config) as manager:
        print(f"\n🚀 Starting concurrent analysis of {len(test_symbols)} stocks...")
        
        results = manager.execute_concurrent(
            test_symbols,
            mock_analyze_stock,
            progress_callback
        )
    
    end_time = time.time()
    
    # Analyze results
    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]
    
    print(f"\n📊 Test results:")
    print(f"   Total time: {end_time - start_time:.2f}s")
    print(f"   Success: {len(successful_results)}/{len(test_symbols)}")
    print(f"   Failed: {len(failed_results)}")
    print(f"   Success rate: {len(successful_results)/len(test_symbols)*100:.1f}%")
    
    # Show failure details
    if failed_results:
        print(f"\n❌ Failure details:")
        for result in failed_results:
            print(f"   • {result.symbol}: {result.error}")
    
    # Average processing time
    if successful_results:
        avg_duration = sum((r.duration.total_seconds() for r in successful_results if r.duration), 0.0) / len(successful_results)
        print(f"📈 Average processing time: {avg_duration:.2f}s")


if __name__ == "__main__":
    test_concurrent_manager()