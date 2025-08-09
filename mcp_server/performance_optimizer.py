#!/usr/bin/env python3
"""
Performance Optimization Module for DevOps MCP Server
Implements Cursor AI techniques and industry best practices for performance
"""

import asyncio
import functools
import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple, Callable
import threading
from collections import defaultdict, deque
import weakref
import gc

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    operation: str
    duration: float
    memory_usage: int
    cpu_usage: float
    cache_hit: bool
    timestamp: float
    success: bool
    error_message: Optional[str] = None

class LRUCache:
    """High-performance LRU Cache implementation"""
    
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache = {}
        self.access_order = deque()
        self.timestamps = {}
        self._lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with TTL check"""
        with self._lock:
            current_time = time.time()
            
            # Check if key exists and is not expired
            if key in self.cache:
                if current_time - self.timestamps[key] < self.ttl:
                    # Move to end (most recently used)
                    self.access_order.remove(key)
                    self.access_order.append(key)
                    self.stats['hits'] += 1
                    return self.cache[key]
                else:
                    # Expired, remove
                    self._remove_key(key)
                    self.stats['expired'] += 1
            
            self.stats['misses'] += 1
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache"""
        with self._lock:
            current_time = time.time()
            
            if key in self.cache:
                # Update existing
                self.access_order.remove(key)
            elif len(self.cache) >= self.maxsize:
                # Evict least recently used
                oldest_key = self.access_order.popleft()
                self._remove_key(oldest_key)
                self.stats['evictions'] += 1
            
            self.cache[key] = value
            self.timestamps[key] = current_time
            self.access_order.append(key)
    
    def _remove_key(self, key: str) -> None:
        """Remove key from cache"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.timestamps.clear()
            self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                **self.stats,
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'cache_size': len(self.cache)
            }

class PromptOptimizer:
    """Optimizes prompts using Cursor AI techniques"""
    
    def __init__(self):
        self.optimization_cache = LRUCache(maxsize=500, ttl=7200)  # 2 hours TTL
        self.performance_history = deque(maxlen=1000)
        self.optimization_patterns = {
            'redundant_phrases': [
                'please', 'could you', 'would you mind', 'if possible',
                'I need you to', 'can you help me', 'I would like'
            ],
            'filler_words': [
                'actually', 'basically', 'essentially', 'literally',
                'obviously', 'definitely', 'certainly'
            ],
            'verbose_patterns': [
                ('in order to', 'to'),
                ('due to the fact that', 'because'),
                ('at this point in time', 'now'),
                ('in the event that', 'if'),
                ('for the purpose of', 'for')
            ]
        }
    
    def optimize_prompt(self, prompt: str, domain: str) -> Tuple[str, Dict[str, Any]]:
        """Optimize prompt for better performance and clarity"""
        cache_key = hashlib.md5(f"{prompt}:{domain}".encode()).hexdigest()
        
        # Check cache first
        cached_result = self.optimization_cache.get(cache_key)
        if cached_result:
            return cached_result['optimized_prompt'], cached_result['metrics']
        
        start_time = time.time()
        original_length = len(prompt)
        
        optimized = prompt
        optimizations_applied = []
        
        # Remove redundant phrases
        for phrase in self.optimization_patterns['redundant_phrases']:
            if phrase in optimized.lower():
                optimized = optimized.replace(phrase, '')
                optimizations_applied.append(f"removed_redundant: {phrase}")
        
        # Remove filler words
        for word in self.optimization_patterns['filler_words']:
            pattern = f" {word} "
            if pattern in optimized.lower():
                optimized = optimized.replace(pattern, ' ')
                optimizations_applied.append(f"removed_filler: {word}")
        
        # Replace verbose patterns
        for verbose, concise in self.optimization_patterns['verbose_patterns']:
            if verbose in optimized.lower():
                optimized = optimized.replace(verbose, concise)
                optimizations_applied.append(f"simplified: {verbose} -> {concise}")
        
        # Domain-specific optimizations
        if domain == 'devops':
            optimized = self._optimize_devops_prompt(optimized)
            optimizations_applied.append("applied_devops_optimizations")
        elif domain == 'sre':
            optimized = self._optimize_sre_prompt(optimized)
            optimizations_applied.append("applied_sre_optimizations")
        elif domain == 'cloud':
            optimized = self._optimize_cloud_prompt(optimized)
            optimizations_applied.append("applied_cloud_optimizations")
        elif domain == 'platform':
            optimized = self._optimize_platform_prompt(optimized)
            optimizations_applied.append("applied_platform_optimizations")
        
        # Clean up extra whitespace
        optimized = ' '.join(optimized.split())
        
        optimization_time = time.time() - start_time
        optimized_length = len(optimized)
        compression_ratio = 1 - (optimized_length / original_length)
        
        metrics = {
            'original_length': original_length,
            'optimized_length': optimized_length,
            'compression_ratio': compression_ratio,
            'optimization_time': optimization_time,
            'optimizations_applied': optimizations_applied,
            'domain': domain
        }
        
        # Cache the result
        result = {
            'optimized_prompt': optimized,
            'metrics': metrics
        }
        self.optimization_cache.put(cache_key, result)
        
        # Track performance
        self.performance_history.append(PerformanceMetrics(
            operation='prompt_optimization',
            duration=optimization_time,
            memory_usage=0,  # TODO: Implement memory tracking
            cpu_usage=0.0,  # TODO: Implement CPU tracking
            cache_hit=False,
            timestamp=time.time(),
            success=True
        ))
        
        return optimized, metrics
    
    def _optimize_devops_prompt(self, prompt: str) -> str:
        """Apply DevOps-specific optimizations"""
        # Add structured format hints
        if 'analyze' in prompt.lower() and 'json' not in prompt.lower():
            prompt += "\n\nProvide response in structured JSON format with clear sections for analysis, recommendations, and implementation steps."
        
        # Emphasize actionable outputs
        if 'recommend' in prompt.lower():
            prompt += "\n\nFocus on actionable, production-ready solutions with specific commands and configurations."
        
        return prompt
    
    def _optimize_sre_prompt(self, prompt: str) -> str:
        """Apply SRE-specific optimizations"""
        # Add SLO/SLI context
        if 'incident' in prompt.lower() or 'outage' in prompt.lower():
            prompt += "\n\nInclude SLO impact analysis and error budget implications in your response."
        
        # Emphasize quantitative metrics
        if 'performance' in prompt.lower():
            prompt += "\n\nProvide quantitative metrics and measurable targets in your analysis."
        
        return prompt
    
    def _optimize_cloud_prompt(self, prompt: str) -> str:
        """Apply Cloud-specific optimizations"""
        # Add cost considerations
        if 'architecture' in prompt.lower() or 'design' in prompt.lower():
            prompt += "\n\nInclude cost implications and optimization opportunities in your recommendations."
        
        # Emphasize security and compliance
        if 'migration' in prompt.lower() or 'deployment' in prompt.lower():
            prompt += "\n\nAddress security, compliance, and governance considerations."
        
        return prompt
    
    def _optimize_platform_prompt(self, prompt: str) -> str:
        """Apply Platform Engineering-specific optimizations"""
        # Add developer experience focus
        if 'platform' in prompt.lower() or 'developer' in prompt.lower():
            prompt += "\n\nPrioritize developer experience and productivity in your recommendations."
        
        # Emphasize self-service capabilities
        if 'tool' in prompt.lower() or 'service' in prompt.lower():
            prompt += "\n\nFocus on self-service capabilities and automation opportunities."
        
        return prompt

class ResponseStreamer:
    """Implements response streaming for better perceived performance"""
    
    def __init__(self):
        self.chunk_size = 100  # characters per chunk
        self.delay = 0.05  # seconds between chunks
    
    async def stream_response(self, response: str, callback: Callable[[str], None]) -> None:
        """Stream response in chunks"""
        chunks = [response[i:i+self.chunk_size] for i in range(0, len(response), self.chunk_size)]
        
        for chunk in chunks:
            callback(chunk)
            await asyncio.sleep(self.delay)

class ParallelProcessor:
    """Implements parallel processing for multiple operations"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=max_workers)
    
    async def process_parallel_analyses(self, analyses: List[Dict[str, Any]]) -> List[Any]:
        """Process multiple analyses in parallel"""
        loop = asyncio.get_event_loop()
        
        # Create tasks for parallel execution
        tasks = []
        for analysis in analyses:
            if analysis.get('cpu_intensive', False):
                # Use process executor for CPU-intensive tasks
                task = loop.run_in_executor(
                    self.process_executor,
                    self._cpu_intensive_analysis,
                    analysis
                )
            else:
                # Use thread executor for I/O-bound tasks
                task = loop.run_in_executor(
                    self.thread_executor,
                    self._io_bound_analysis,
                    analysis
                )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Analysis {i} failed: {result}")
                processed_results.append({
                    'error': str(result),
                    'analysis_id': analyses[i].get('id', f'analysis_{i}')
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _cpu_intensive_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for CPU-intensive analysis"""
        # Simulate CPU-intensive work
        time.sleep(0.1)
        return {
            'analysis_id': analysis.get('id'),
            'result': 'cpu_intensive_result',
            'processing_time': 0.1
        }
    
    def _io_bound_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for I/O-bound analysis"""
        # Simulate I/O-bound work
        time.sleep(0.05)
        return {
            'analysis_id': analysis.get('id'),
            'result': 'io_bound_result',
            'processing_time': 0.05
        }

class ContextCompressor:
    """Compresses context to reduce token usage while maintaining quality"""
    
    def __init__(self):
        self.compression_cache = LRUCache(maxsize=200, ttl=1800)  # 30 minutes TTL
    
    def compress_context(self, context: str, target_reduction: float = 0.3) -> Tuple[str, Dict[str, Any]]:
        """Compress context while preserving important information"""
        cache_key = hashlib.md5(f"{context}:{target_reduction}".encode()).hexdigest()
        
        cached_result = self.compression_cache.get(cache_key)
        if cached_result:
            return cached_result['compressed'], cached_result['metrics']
        
        start_time = time.time()
        original_length = len(context)
        
        # Extract key information
        key_phrases = self._extract_key_phrases(context)
        structured_info = self._extract_structured_info(context)
        
        # Build compressed version
        compressed_parts = []
        
        # Add essential structured information
        if structured_info:
            compressed_parts.append("Key Information:")
            for category, items in structured_info.items():
                if items:
                    compressed_parts.append(f"- {category}: {', '.join(items[:3])}")
        
        # Add most important phrases
        if key_phrases:
            compressed_parts.append("\nImportant Details:")
            compressed_parts.extend([f"- {phrase}" for phrase in key_phrases[:10]])
        
        compressed = "\n".join(compressed_parts)
        
        # Ensure we meet the target reduction
        current_reduction = 1 - (len(compressed) / original_length)
        if current_reduction < target_reduction:
            # Further compress by removing less important details
            compressed = self._aggressive_compress(compressed, target_reduction)
        
        compression_time = time.time() - start_time
        final_length = len(compressed)
        actual_reduction = 1 - (final_length / original_length)
        
        metrics = {
            'original_length': original_length,
            'compressed_length': final_length,
            'reduction_ratio': actual_reduction,
            'target_reduction': target_reduction,
            'compression_time': compression_time,
            'key_phrases_count': len(key_phrases),
            'structured_info_categories': len(structured_info)
        }
        
        result = {
            'compressed': compressed,
            'metrics': metrics
        }
        self.compression_cache.put(cache_key, result)
        
        return compressed, metrics
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        # Simple keyword extraction (can be enhanced with NLP libraries)
        important_indicators = [
            'error', 'critical', 'high', 'urgent', 'failed', 'down',
            'performance', 'latency', 'throughput', 'availability',
            'security', 'vulnerability', 'breach', 'compliance',
            'cost', 'optimization', 'scaling', 'capacity'
        ]
        
        sentences = text.split('.')
        key_phrases = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in important_indicators):
                if len(sentence) < 200:  # Keep only concise sentences
                    key_phrases.append(sentence)
        
        return key_phrases[:15]  # Limit to top 15 phrases
    
    def _extract_structured_info(self, text: str) -> Dict[str, List[str]]:
        """Extract structured information from text"""
        structured = {
            'services': [],
            'metrics': [],
            'errors': [],
            'recommendations': []
        }
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract service names
            if 'service' in line.lower():
                words = line.split()
                for word in words:
                    if 'service' in word.lower() and len(word) > 7:
                        structured['services'].append(word)
            
            # Extract metrics
            if any(metric in line.lower() for metric in ['cpu', 'memory', 'disk', 'network', 'latency']):
                structured['metrics'].append(line)
            
            # Extract errors
            if any(error in line.lower() for error in ['error', 'failed', 'exception', 'timeout']):
                structured['errors'].append(line)
            
            # Extract recommendations
            if line.startswith('-') or line.startswith('*') or 'recommend' in line.lower():
                structured['recommendations'].append(line)
        
        # Deduplicate and limit
        for key in structured:
            structured[key] = list(set(structured[key]))[:5]
        
        return structured
    
    def _aggressive_compress(self, text: str, target_reduction: float) -> str:
        """Apply aggressive compression techniques"""
        # Remove redundant words and phrases
        lines = text.split('\n')
        compressed_lines = []
        
        for line in lines:
            # Remove common redundant phrases
            line = line.replace('in order to', 'to')
            line = line.replace('due to the fact that', 'because')
            line = line.replace('at this point in time', 'now')
            
            # Keep only essential information
            if len(line.strip()) > 10:  # Skip very short lines
                compressed_lines.append(line)
        
        return '\n'.join(compressed_lines)

class PerformanceMonitor:
    """Monitors and tracks performance metrics"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=10000)
        self.alert_thresholds = {
            'response_time': 5.0,  # seconds
            'memory_usage': 1000000000,  # 1GB
            'cache_hit_rate': 0.8,  # 80%
            'error_rate': 0.05  # 5%
        }
        self._lock = threading.Lock()
    
    def record_metric(self, metric: PerformanceMetrics) -> None:
        """Record a performance metric"""
        with self._lock:
            self.metrics_history.append(metric)
            self._check_alerts(metric)
    
    def get_performance_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get performance summary for the specified time window"""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        with self._lock:
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {'error': 'No metrics available for the specified time window'}
        
        # Calculate summary statistics
        response_times = [m.duration for m in recent_metrics]
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.success)
        
        return {
            'time_window': time_window,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests,
            'cache_hit_rate': cache_hits / total_requests,
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': self._percentile(response_times, 95),
            'p99_response_time': self._percentile(response_times, 99),
            'operations': self._get_operation_breakdown(recent_metrics)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _get_operation_breakdown(self, metrics: List[PerformanceMetrics]) -> Dict[str, Dict[str, Any]]:
        """Get breakdown by operation type"""
        operations = defaultdict(list)
        
        for metric in metrics:
            operations[metric.operation].append(metric)
        
        breakdown = {}
        for operation, op_metrics in operations.items():
            durations = [m.duration for m in op_metrics]
            breakdown[operation] = {
                'count': len(op_metrics),
                'avg_duration': sum(durations) / len(durations),
                'success_rate': sum(1 for m in op_metrics if m.success) / len(op_metrics)
            }
        
        return breakdown
    
    def _check_alerts(self, metric: PerformanceMetrics) -> None:
        """Check if metric triggers any alerts"""
        alerts = []
        
        if metric.duration > self.alert_thresholds['response_time']:
            alerts.append(f"High response time: {metric.duration:.2f}s")
        
        if metric.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append(f"High memory usage: {metric.memory_usage / 1000000:.1f}MB")
        
        if not metric.success:
            alerts.append(f"Operation failed: {metric.error_message}")
        
        for alert in alerts:
            logger.warning(f"Performance Alert - {alert}")

class CursorAIOptimizer:
    """Implements Cursor AI-inspired optimization techniques"""
    
    def __init__(self):
        self.prompt_optimizer = PromptOptimizer()
        self.context_compressor = ContextCompressor()
        self.response_streamer = ResponseStreamer()
        self.parallel_processor = ParallelProcessor()
        self.performance_monitor = PerformanceMonitor()
        self.global_cache = LRUCache(maxsize=2000, ttl=7200)
    
    async def optimize_request(self, 
                             prompt: str, 
                             context: str, 
                             domain: str,
                             enable_streaming: bool = True,
                             enable_compression: bool = True) -> Dict[str, Any]:
        """Apply comprehensive optimization to a request"""
        start_time = time.time()
        
        optimization_results = {
            'original_prompt_length': len(prompt),
            'original_context_length': len(context),
            'optimizations_applied': []
        }
        
        try:
            # 1. Optimize prompt
            optimized_prompt, prompt_metrics = self.prompt_optimizer.optimize_prompt(prompt, domain)
            optimization_results['prompt_optimization'] = prompt_metrics
            optimization_results['optimizations_applied'].append('prompt_optimization')
            
            # 2. Compress context if enabled and needed
            if enable_compression and len(context) > 5000:
                compressed_context, compression_metrics = self.context_compressor.compress_context(context)
                optimization_results['context_compression'] = compression_metrics
                optimization_results['optimizations_applied'].append('context_compression')
                context = compressed_context
            
            # 3. Cache check
            cache_key = hashlib.md5(f"{optimized_prompt}:{context}:{domain}".encode()).hexdigest()
            cached_response = self.global_cache.get(cache_key)
            
            if cached_response:
                optimization_results['cache_hit'] = True
                optimization_results['optimizations_applied'].append('cache_hit')
                
                # Record performance metric
                total_time = time.time() - start_time
                self.performance_monitor.record_metric(PerformanceMetrics(
                    operation='optimize_request',
                    duration=total_time,
                    memory_usage=0,
                    cpu_usage=0.0,
                    cache_hit=True,
                    timestamp=time.time(),
                    success=True
                ))
                
                return {
                    'response': cached_response,
                    'optimization_results': optimization_results,
                    'processing_time': total_time,
                    'cache_hit': True
                }
            
            # 4. Prepare optimized request data
            optimized_request = {
                'prompt': optimized_prompt,
                'context': context,
                'domain': domain,
                'cache_key': cache_key
            }
            
            optimization_results['cache_hit'] = False
            optimization_results['final_prompt_length'] = len(optimized_prompt)
            optimization_results['final_context_length'] = len(context)
            
            total_optimization_time = time.time() - start_time
            optimization_results['optimization_time'] = total_optimization_time
            
            # Record performance metric
            self.performance_monitor.record_metric(PerformanceMetrics(
                operation='optimize_request',
                duration=total_optimization_time,
                memory_usage=0,
                cpu_usage=0.0,
                cache_hit=False,
                timestamp=time.time(),
                success=True
            ))
            
            return {
                'optimized_request': optimized_request,
                'optimization_results': optimization_results,
                'processing_time': total_optimization_time,
                'cache_hit': False
            }
            
        except Exception as e:
            logger.error(f"Request optimization failed: {e}")
            
            # Record error metric
            self.performance_monitor.record_metric(PerformanceMetrics(
                operation='optimize_request',
                duration=time.time() - start_time,
                memory_usage=0,
                cpu_usage=0.0,
                cache_hit=False,
                timestamp=time.time(),
                success=False,
                error_message=str(e)
            ))
            
            # Return original request as fallback
            return {
                'optimized_request': {
                    'prompt': prompt,
                    'context': context,
                    'domain': domain,
                    'cache_key': None
                },
                'optimization_results': {'error': str(e)},
                'processing_time': time.time() - start_time,
                'cache_hit': False
            }
    
    def cache_response(self, cache_key: str, response: str) -> None:
        """Cache a response for future use"""
        if cache_key:
            self.global_cache.put(cache_key, response)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'prompt_optimizer_cache': self.prompt_optimizer.optimization_cache.get_stats(),
            'context_compressor_cache': self.context_compressor.compression_cache.get_stats(),
            'global_cache': self.global_cache.get_stats(),
            'performance_summary': self.performance_monitor.get_performance_summary(),
            'memory_usage': self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        # Force garbage collection for accurate measurement
        gc.collect()
        
        return {
            'cache_objects': len(self.global_cache.cache),
            'optimization_history': len(self.prompt_optimizer.performance_history),
            'performance_metrics': len(self.performance_monitor.metrics_history)
        }
    
    async def cleanup_resources(self) -> None:
        """Clean up resources and perform maintenance"""
        logger.info("Performing resource cleanup...")
        
        # Clear expired cache entries
        self.global_cache.clear()
        self.prompt_optimizer.optimization_cache.clear()
        self.context_compressor.compression_cache.clear()
        
        # Force garbage collection
        gc.collect()
        
        logger.info("Resource cleanup completed")

# Global optimizer instance
optimizer = CursorAIOptimizer()

def performance_decorator(operation_name: str):
    """Decorator to automatically track performance metrics"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                optimizer.performance_monitor.record_metric(PerformanceMetrics(
                    operation=operation_name,
                    duration=duration,
                    memory_usage=0,  # TODO: Implement memory tracking
                    cpu_usage=0.0,  # TODO: Implement CPU tracking
                    cache_hit=False,
                    timestamp=time.time(),
                    success=True
                ))
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                optimizer.performance_monitor.record_metric(PerformanceMetrics(
                    operation=operation_name,
                    duration=duration,
                    memory_usage=0,
                    cpu_usage=0.0,
                    cache_hit=False,
                    timestamp=time.time(),
                    success=False,
                    error_message=str(e)
                ))
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                optimizer.performance_monitor.record_metric(PerformanceMetrics(
                    operation=operation_name,
                    duration=duration,
                    memory_usage=0,
                    cpu_usage=0.0,
                    cache_hit=False,
                    timestamp=time.time(),
                    success=True
                ))
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                optimizer.performance_monitor.record_metric(PerformanceMetrics(
                    operation=operation_name,
                    duration=duration,
                    memory_usage=0,
                    cpu_usage=0.0,
                    cache_hit=False,
                    timestamp=time.time(),
                    success=False,
                    error_message=str(e)
                ))
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
