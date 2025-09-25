"""
Batch analyzer for multi-stock analysis

Integrates single stock analyzer and recommendation engine for batch processing logic
"""

import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ..analyzers.stock_analyzer import StockAnalyzer
from ..engines.recommendation_engine import RecommendationEngine
from ..languages.config import LanguageConfig
from .concurrent_manager import ConcurrentManager, ConcurrentConfig, TaskResult, create_optimized_config
from .progress_tracker import ProgressTracker


@dataclass
class BatchAnalysisResult:
    """Batch analysis result"""
    total_stocks: int
    successful_analyses: List[Dict]
    failed_analyses: List[Dict]
    analysis_time: float
    success_rate: float
    
    @property
    def successful_count(self) -> int:
        return len(self.successful_analyses)
    
    @property
    def failed_count(self) -> int:
        return len(self.failed_analyses)


class BatchAnalyzer:
    """Batch stock analyzer"""
    
    def __init__(self, lang_config: Optional[LanguageConfig] = None, period: str = "1y"):
        self.lang_config = lang_config or LanguageConfig('en')
        self.period = period
        self.progress_tracker = None
        
    def analyze_stocks(
        self, 
        symbols: List[str], 
        strategy_type: str = 'combined',
        show_progress: bool = True
    ) -> BatchAnalysisResult:
        """
        Analyze stocks in batch
        
        Args:
            symbols: Stock symbol list
            strategy_type: Analysis strategy type
            show_progress: Whether to show progress
            
        Returns:
            BatchAnalysisResult: Batch analysis result
        """
        start_time = time.time()
        
        print(self.lang_config.get("batch_analysis_start"))
        print(self.lang_config.get("batch_stock_count").format(len(symbols)))
        print(self.lang_config.get("batch_strategy").format(strategy_type))
        print(self.lang_config.get("batch_period").format(self.period))
        print("-" * 50)
        
        # 初始化进度跟踪器
        if show_progress:
            self.progress_tracker = ProgressTracker(self.lang_config)
            self.progress_tracker.initialize(symbols)
            self.progress_tracker.start_display()
        
        # 创建并发配置
        config = create_optimized_config(len(symbols))
        print(self.lang_config.get("batch_concurrent_config").format(config.max_workers, config.api_rate_limit))
        
        # 执行并发分析
        task_results = []
        try:
            with ConcurrentManager(config, self.lang_config) as manager:
                task_results = manager.execute_concurrent(
                    symbols=symbols,
                    task_func=lambda symbol: self._analyze_single_stock(symbol, strategy_type),
                    progress_callback=self._progress_callback
                )
        finally:
            # 停止进度显示
            if show_progress and self.progress_tracker:
                self.progress_tracker.stop_display()
        
        # 处理结果
        successful_analyses = []
        failed_analyses = []
        
        for result in task_results:
            if result.success:
                successful_analyses.append(result.result)
            else:
                failed_analyses.append({
                    'symbol': result.symbol,
                    'error': result.error,
                    'attempts': result.attempts
                })
        
        end_time = time.time()
        analysis_time = end_time - start_time
        success_rate = (len(successful_analyses) / len(symbols)) * 100 if symbols else 0
        
        # 创建结果对象
        batch_result = BatchAnalysisResult(
            total_stocks=len(symbols),
            successful_analyses=successful_analyses,
            failed_analyses=failed_analyses,
            analysis_time=analysis_time,
            success_rate=success_rate
        )
        
        # 显示总结
        if show_progress and self.progress_tracker:
            self.progress_tracker.print_summary(self._format_friendly_error)
        else:
            self._print_simple_summary(batch_result)
        
        return batch_result
    
    def _analyze_single_stock(self, symbol: str, strategy_type: str) -> Dict:
        """
        分析单只股票
        
        Args:
            symbol: 股票代码
            strategy_type: 策略类型
            
        Returns:
            Dict: 分析结果
        """
        try:
            # 创建股票分析器
            analyzer = StockAnalyzer(symbol, self.lang_config)
            analyzer.fetch_data(self.period)
            
            # 创建推荐引擎
            engine = RecommendationEngine(analyzer, self.lang_config)
            
            # 生成推荐
            recommendation = engine.generate_recommendation(strategy_type=strategy_type)
            
            return recommendation
            
        except Exception as e:
            raise Exception(f"股票 {symbol} 分析失败: {str(e)}")
    
    def _progress_callback(self, symbol: str, status: str):
        """进度回调函数"""
        if self.progress_tracker:
            if status == "running":
                self.progress_tracker.start_task(symbol)
            elif status == "completed":
                # 这里需要实际的结果，但为了简化，我们传入空dict
                self.progress_tracker.complete_task(symbol, {})
            elif status == "failed":
                self.progress_tracker.fail_task(symbol, "分析失败")
    
    def _print_simple_summary(self, result: BatchAnalysisResult):
        """打印简单总结"""
        print(f"\n" + "="*50)
        print(self.lang_config.get("batch_analysis_complete"))
        print("="*50)
        print(self.lang_config.get("batch_total_stocks").format(result.total_stocks))
        print(self.lang_config.get("batch_success_rate").format(result.successful_count, result.success_rate))
        print(self.lang_config.get("batch_failed_count").format(result.failed_count))
        print(self.lang_config.get("batch_total_time").format(result.analysis_time))
        
        if result.failed_analyses:
            print(f"\n{self.lang_config.get('batch_failed_details')}")
            for failure in result.failed_analyses:
                error_msg = self._format_friendly_error(failure['symbol'], failure['error'])
                print(f"   • {error_msg}")
        
        print("="*50)
    
    def _format_friendly_error(self, symbol: str, error: str) -> str:
        """格式化友好的错误信息"""
        # 检查是否包含"delisted"关键词或网络错误
        if 'delisted' in error.lower() or 'no data found' in error.lower():
            return self.lang_config.get("error_stock_delisted").format(symbol)
        
        # 检查是否是网络相关错误
        if 'timeout' in error.lower() or 'connection' in error.lower():
            return self.lang_config.get("error_network_issue").format(symbol)
        
        # 默认错误信息
        return f"{symbol}: {error}"
    



def test_batch_analyzer():
    """Test batch analyzer"""
    print("🧪 Testing batch analyzer...")
    
    # Test symbol list
    test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    
    # Create analyzer
    lang_config = LanguageConfig('en')
    analyzer = BatchAnalyzer(lang_config, period='6mo')  # Use shorter period for faster testing
    
    # Execute batch analysis
    print(f"\n🔍 Starting analysis of {len(test_symbols)} stocks...")
    
    try:
        result = analyzer.analyze_stocks(
            symbols=test_symbols,
            strategy_type='technical',  # Use technical analysis strategy
            show_progress=True
        )
        
        print(f"\n✅ Test completed!")
        print(f"   Successfully analyzed: {result.successful_count}")
        print(f"   Failed: {result.failed_count}")
        print(f"   Success rate: {result.success_rate:.1f}%")
        
        # Display partial successful results
        if result.successful_analyses:
            print(f"\n📋 Successfully analyzed stocks:")
            for analysis in result.successful_analyses[:3]:  # Show first 3
                print(f"   • {analysis['symbol']}: {analysis['recommendation']['action']} "
                      f"(Score: {analysis['recommendation']['score']})")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    test_batch_analyzer()