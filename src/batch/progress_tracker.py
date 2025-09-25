"""
Progress tracker for multi-stock analysis

Provides real-time progress display, statistics, and user-friendly progress bars
"""

import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class AnalysisTask:
    """Individual analysis task"""
    symbol: str
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict] = None
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get task execution time"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass 
class ProgressStats:
    """Progress statistics information"""
    total_tasks: int = 0
    completed: int = 0
    failed: int = 0
    running: int = 0
    pending: int = 0
    start_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Success rate"""
        if self.completed + self.failed == 0:
            return 0.0
        return (self.completed / (self.completed + self.failed)) * 100
    
    @property
    def completion_rate(self) -> float:
        """Completion rate"""
        if self.total_tasks == 0:
            return 0.0
        return ((self.completed + self.failed) / self.total_tasks) * 100
    
    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Elapsed time"""
        if self.start_time:
            return datetime.now() - self.start_time
        return None
    
    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        """Estimated remaining time"""
        if not self.start_time or self.completed == 0:
            return None
        
        elapsed = self.elapsed_time
        if not elapsed:
            return None
        
        avg_time_per_task = elapsed / self.completed
        remaining_tasks = self.total_tasks - self.completed - self.failed
        
        return avg_time_per_task * remaining_tasks


class ProgressTracker:
    """Progress tracker"""
    
    def __init__(self, lang_config=None):
        self.lang_config = lang_config
        self.tasks: Dict[str, AnalysisTask] = {}
        self.stats = ProgressStats()
        self._lock = threading.Lock()
        self._display_thread = None
        self._stop_display = False
        self._last_display_time = 0
        
    def initialize(self, symbols: List[str]):
        """Initialize task list"""
        with self._lock:
            self.tasks.clear()
            self.stats = ProgressStats(total_tasks=len(symbols))
            self.stats.pending = len(symbols)
            self.stats.start_time = datetime.now()
            
            for symbol in symbols:
                self.tasks[symbol] = AnalysisTask(symbol=symbol)
    
    def start_task(self, symbol: str):
        """Start task"""
        with self._lock:
            if symbol in self.tasks:
                task = self.tasks[symbol]
                task.status = "running"
                task.start_time = datetime.now()
                
                # Update statistics
                self.stats.pending -= 1
                self.stats.running += 1
    
    def complete_task(self, symbol: str, result: Dict):
        """Complete task"""
        with self._lock:
            if symbol in self.tasks:
                task = self.tasks[symbol]
                task.status = "completed"
                task.end_time = datetime.now()
                task.result = result
                
                # Update statistics
                self.stats.running -= 1
                self.stats.completed += 1
    
    def fail_task(self, symbol: str, error: str):
        """Task failed"""
        with self._lock:
            if symbol in self.tasks:
                task = self.tasks[symbol]
                task.status = "failed"
                task.end_time = datetime.now()
                task.error_message = error
                
                # Update statistics
                self.stats.running -= 1
                self.stats.failed += 1
    
    def get_current_stats(self) -> ProgressStats:
        """Get current statistics"""
        with self._lock:
            return ProgressStats(
                total_tasks=self.stats.total_tasks,
                completed=self.stats.completed,
                failed=self.stats.failed,
                running=self.stats.running,
                pending=self.stats.pending,
                start_time=self.stats.start_time
            )
    
    def get_completed_results(self) -> List[Dict]:
        """Get all completed results"""
        with self._lock:
            results = []
            for task in self.tasks.values():
                if task.status == "completed" and task.result:
                    results.append(task.result)
            return results
    
    def get_failed_tasks(self) -> List[AnalysisTask]:
        """Get failed tasks"""
        with self._lock:
            return [task for task in self.tasks.values() if task.status == "failed"]
    
    def start_display(self, update_interval: float = 0.5):
        """Start progress display"""
        self._stop_display = False
        self._display_thread = threading.Thread(target=self._display_loop, args=(update_interval,))
        self._display_thread.daemon = True
        self._display_thread.start()
    
    def stop_display(self):
        """Stop progress display"""
        self._stop_display = True
        if self._display_thread:
            self._display_thread.join(timeout=1.0)
    
    def _display_loop(self, update_interval: float):
        """Progress display loop"""
        while not self._stop_display:
            current_time = time.time()
            if current_time - self._last_display_time >= update_interval:
                self._update_display()
                self._last_display_time = current_time
            time.sleep(0.1)
    
    def _update_display(self):
        """Update progress display"""
        stats = self.get_current_stats()
        
        # Create progress bar
        progress_bar = self._create_progress_bar(stats.completion_rate)
        
        # Format time information
        elapsed_str = self._format_duration(stats.elapsed_time) if stats.elapsed_time else "0s"
        remaining_text = self.lang_config.get("progress_calculating") if self.lang_config else "Calculating..."
        remaining_str = self._format_duration(stats.estimated_remaining) if stats.estimated_remaining else remaining_text
        
        # Create status line
        remaining_label = self.lang_config.get('progress_estimated_remaining').replace("{}", remaining_str) if self.lang_config else f'Estimated remaining: {remaining_str}'
        status_line = (
            f"\r📊 Progress: {progress_bar} "
            f"{stats.completed + stats.failed}/{stats.total_tasks} "
            f"({stats.completion_rate:.1f}%) | "
            f"✅{stats.completed} ❌{stats.failed} 🔄{stats.running} ⏳{stats.pending} | "
            f"Elapsed: {elapsed_str} | "
            f"{remaining_label}"
        )
        
        # Output status line
        print(status_line, end="", flush=True)
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration"""
        if not duration:
            return "0s"
        
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m{seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h{minutes}m"
    
    def print_summary(self, error_formatter=None):
        """Print analysis summary"""
        stats = self.get_current_stats()
        print("\n" + "="*60)
        print(self.lang_config.get("batch_analysis_summary") if self.lang_config else "📈 Multi-stock analysis summary")
        print("="*60)
        
        # Basic statistics
        if self.lang_config:
            total_text = self.lang_config.get("batch_total_stocks").format(stats.total_tasks)
        else:
            total_text = f"Total stocks: {stats.total_tasks}"
        print(f"📊 {total_text}")
        
        success_text = self.lang_config.get("batch_success_rate") if self.lang_config else "✅ Success: {} ({:.1f}%)"
        print(success_text.format(stats.completed, stats.success_rate))
        
        if self.lang_config:
            failed_text = self.lang_config.get("batch_failed_count").format(stats.failed)
        else:
            failed_text = f"❌ Failed: {stats.failed}"
        print(failed_text)
        
        elapsed_duration = self._format_duration(stats.elapsed_time) if stats.elapsed_time else '0s'
        if self.lang_config:
            time_text = self.lang_config.get("batch_total_time").format(elapsed_duration)
        else:
            time_text = f"⏱️  Total time: {elapsed_duration}"
        print(time_text)
        
        # Failed task details
        failed_tasks = self.get_failed_tasks()
        if failed_tasks:
            failed_details_text = self.lang_config.get("batch_failed_details") if self.lang_config else "❌ Failed task details:"
            print(f"\n{failed_details_text}")
            for task in failed_tasks:
                if error_formatter:
                    formatted_error = error_formatter(task.symbol, task.error_message)
                    print(f"   • {formatted_error}")
                else:
                    print(f"   • {task.symbol}: {task.error_message}")
        
        # Performance statistics
        if stats.completed > 0 and stats.elapsed_time:
            avg_time = stats.elapsed_time / stats.completed
            avg_duration = self._format_duration(avg_time)
            if self.lang_config:
                avg_time_text = self.lang_config.get("batch_avg_time").format(avg_duration)
                print(avg_time_text)
            else:
                print(f"📈 Average processing time: {avg_duration}")
        
        print("="*60)
    
    def get_running_tasks(self) -> List[str]:
        """Get list of running task symbols"""
        with self._lock:
            return [symbol for symbol, task in self.tasks.items() if task.status == "running"]
    
    def is_completed(self) -> bool:
        """Check if all tasks are completed"""
        with self._lock:
            return self.stats.pending == 0 and self.stats.running == 0


def test_progress_tracker():
    """Test progress tracker"""
    print("🧪 Testing progress tracker...")
    
    # Create test stock list
    test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    
    # Initialize tracker
    tracker = ProgressTracker()
    tracker.initialize(test_symbols)
    
    print(f"Initialized {len(test_symbols)} tasks")
    
    # Start progress display
    tracker.start_display()
    
    # Simulate task execution
    for i, symbol in enumerate(test_symbols):
        tracker.start_task(symbol)
        print(f"\nStarting analysis for {symbol}...")
        
        # Simulate analysis time
        time.sleep(0.5)
        
        # Randomly decide success or failure
        import random
        if random.random() > 0.2:  # 80% success rate
            result = {
                "symbol": symbol,
                "recommendation": "Buy",
                "score": random.randint(50, 100)
            }
            tracker.complete_task(symbol, result)
        else:
            tracker.fail_task(symbol, f"Simulation error - {symbol} data fetch failed")
    
    # Wait for display update
    time.sleep(1)
    
    # Stop display and print summary
    tracker.stop_display()
    tracker.print_summary()
    
    # Verify results
    stats = tracker.get_current_stats()
    print(f"\n✅ Test completed:")
    print(f"   Completed tasks: {stats.completed}")
    print(f"   Failed tasks: {stats.failed}")
    print(f"   Success rate: {stats.success_rate:.1f}%")


if __name__ == "__main__":
    test_progress_tracker()