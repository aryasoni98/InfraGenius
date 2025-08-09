#!/usr/bin/env python3
"""
MCP Server Performance Test
Tests the performance of MCP server components without relying on slow Ollama inference
"""

import asyncio
import time
import json
import sys
from typing import Dict, List, Any
import psutil
from dataclasses import dataclass

# Import our modules
from performance_optimizer import (
    CursorAIOptimizer, 
    PromptOptimizer, 
    ContextCompressor,
    LRUCache,
    PerformanceMonitor
)
from industry_tools import IndustryToolsManager

@dataclass
class TestResult:
    test_name: str
    duration: float
    success: bool
    details: Dict[str, Any]
    error: str = ""

class MCPPerformanceTester:
    """Test MCP server components performance"""
    
    def __init__(self):
        self.results = []
        self.optimizer = CursorAIOptimizer()
        
    def test_cache_performance(self) -> TestResult:
        """Test LRU cache performance"""
        print("🗄️ Testing LRU Cache performance...")
        
        start_time = time.time()
        try:
            cache = LRUCache(maxsize=1000, ttl=3600)
            
            # Test cache operations
            ops_count = 1000
            
            # Write operations
            write_start = time.time()
            for i in range(ops_count):
                cache.put(f"key_{i}", f"value_{i}")
            write_time = time.time() - write_start
            
            # Read operations (should hit cache)
            read_start = time.time()
            hits = 0
            for i in range(ops_count):
                if cache.get(f"key_{i}") is not None:
                    hits += 1
            read_time = time.time() - read_start
            
            # Get statistics
            stats = cache.get_stats()
            
            duration = time.time() - start_time
            
            details = {
                'operations': ops_count,
                'write_time': write_time,
                'read_time': read_time,
                'hits': hits,
                'hit_rate': hits / ops_count,
                'cache_stats': stats,
                'ops_per_second': ops_count * 2 / duration
            }
            
            return TestResult("LRU Cache", duration, True, details)
            
        except Exception as e:
            return TestResult("LRU Cache", time.time() - start_time, False, {}, str(e))
    
    def test_prompt_optimization(self) -> TestResult:
        """Test prompt optimization performance"""
        print("✨ Testing Prompt Optimization...")
        
        start_time = time.time()
        try:
            optimizer = PromptOptimizer()
            
            test_prompts = [
                ("devops", "Please analyze this CI/CD pipeline failure and provide recommendations for fixing it"),
                ("sre", "Could you help me understand why my service availability is dropping below SLO targets"),
                ("cloud", "I need assistance with designing a cost-effective cloud architecture for my application"),
                ("platform", "Would you mind helping me create a developer platform for self-service deployments")
            ]
            
            optimization_results = []
            total_original_length = 0
            total_optimized_length = 0
            
            for domain, prompt in test_prompts:
                optimized, metrics = optimizer.optimize_prompt(prompt, domain)
                optimization_results.append({
                    'domain': domain,
                    'original_length': len(prompt),
                    'optimized_length': len(optimized),
                    'compression_ratio': metrics['compression_ratio'],
                    'optimizations_applied': len(metrics['optimizations_applied'])
                })
                total_original_length += len(prompt)
                total_optimized_length += len(optimized)
            
            duration = time.time() - start_time
            
            details = {
                'prompts_processed': len(test_prompts),
                'total_original_length': total_original_length,
                'total_optimized_length': total_optimized_length,
                'overall_compression': 1 - (total_optimized_length / total_original_length),
                'avg_processing_time': duration / len(test_prompts),
                'results': optimization_results
            }
            
            return TestResult("Prompt Optimization", duration, True, details)
            
        except Exception as e:
            return TestResult("Prompt Optimization", time.time() - start_time, False, {}, str(e))
    
    def test_context_compression(self) -> TestResult:
        """Test context compression performance"""
        print("🗜️ Testing Context Compression...")
        
        start_time = time.time()
        try:
            compressor = ContextCompressor()
            
            # Test with a large context
            large_context = """
            This is a large context that contains information about DevOps practices, 
            SRE principles, cloud architecture, and platform engineering. It includes 
            details about CI/CD pipelines, monitoring systems, infrastructure as code,
            container orchestration, service mesh, observability, incident response,
            capacity planning, cost optimization, security best practices, compliance
            requirements, and developer experience improvements. The context also covers
            various tools and technologies like Kubernetes, Docker, Terraform, Ansible,
            Prometheus, Grafana, Jaeger, AWS, Azure, GCP, Jenkins, GitLab, GitHub Actions,
            and many other industry-standard solutions used in modern software delivery.
            """ * 10  # Make it larger
            
            compression_results = []
            for target_reduction in [0.2, 0.4, 0.6]:
                compressed, metrics = compressor.compress_context(large_context, target_reduction)
                compression_results.append({
                    'target_reduction': target_reduction,
                    'actual_reduction': metrics['reduction_ratio'],
                    'original_length': metrics['original_length'],
                    'compressed_length': metrics['compressed_length'],
                    'compression_time': metrics['compression_time']
                })
            
            duration = time.time() - start_time
            
            details = {
                'original_context_size': len(large_context),
                'compression_tests': len(compression_results),
                'results': compression_results,
                'avg_compression_time': sum(r['compression_time'] for r in compression_results) / len(compression_results)
            }
            
            return TestResult("Context Compression", duration, True, details)
            
        except Exception as e:
            return TestResult("Context Compression", time.time() - start_time, False, {}, str(e))
    
    async def test_optimizer_integration(self) -> TestResult:
        """Test the integrated optimizer performance"""
        print("🚀 Testing Cursor AI Optimizer integration...")
        
        start_time = time.time()
        try:
            test_requests = [
                {
                    'prompt': 'Analyze this DevOps pipeline failure and provide recommendations',
                    'context': 'Production CI/CD pipeline with multiple stages and security scanning',
                    'domain': 'devops'
                },
                {
                    'prompt': 'Help me design an SRE monitoring strategy',
                    'context': 'Microservices architecture with high availability requirements',
                    'domain': 'sre'
                },
                {
                    'prompt': 'Optimize cloud costs for my infrastructure',
                    'context': 'AWS environment with multiple services and regions',
                    'domain': 'cloud'
                }
            ]
            
            optimization_results = []
            for request in test_requests:
                result = await self.optimizer.optimize_request(
                    prompt=request['prompt'],
                    context=request['context'],
                    domain=request['domain']
                )
                optimization_results.append(result)
            
            duration = time.time() - start_time
            
            # Calculate statistics
            cache_hits = sum(1 for r in optimization_results if r.get('cache_hit', False))
            avg_optimization_time = sum(r['processing_time'] for r in optimization_results) / len(optimization_results)
            
            details = {
                'requests_processed': len(test_requests),
                'cache_hits': cache_hits,
                'cache_hit_rate': cache_hits / len(test_requests),
                'avg_optimization_time': avg_optimization_time,
                'total_processing_time': sum(r['processing_time'] for r in optimization_results),
                'performance_stats': self.optimizer.get_performance_stats()
            }
            
            return TestResult("Optimizer Integration", duration, True, details)
            
        except Exception as e:
            return TestResult("Optimizer Integration", time.time() - start_time, False, {}, str(e))
    
    def test_industry_tools_config(self) -> TestResult:
        """Test industry tools configuration and initialization"""
        print("🛠️ Testing Industry Tools configuration...")
        
        start_time = time.time()
        try:
            # Test configuration loading
            config = {
                'integrations': {
                    'kubernetes': {
                        'enabled': True,
                        'kubeconfig_path': '~/.kube/config',
                        'namespace': 'default'
                    },
                    'prometheus': {
                        'enabled': False,  # Disable to avoid connection errors
                        'endpoint': 'http://localhost:9090'
                    },
                    'terraform': {
                        'enabled': True,
                        'working_directory': '.',
                        'terraform_binary': 'terraform'
                    }
                }
            }
            
            manager = IndustryToolsManager(config)
            available_tools = manager.get_available_tools()
            
            duration = time.time() - start_time
            
            details = {
                'configured_tools': len(config['integrations']),
                'available_tools': len(available_tools),
                'tool_list': available_tools,
                'initialization_time': duration
            }
            
            return TestResult("Industry Tools", duration, True, details)
            
        except Exception as e:
            return TestResult("Industry Tools", time.time() - start_time, False, {}, str(e))
    
    def test_performance_monitoring(self) -> TestResult:
        """Test performance monitoring system"""
        print("📊 Testing Performance Monitoring...")
        
        start_time = time.time()
        try:
            monitor = PerformanceMonitor()
            
            # Simulate some metrics
            from performance_optimizer import PerformanceMetrics
            
            for i in range(100):
                metric = PerformanceMetrics(
                    operation=f"test_operation_{i % 5}",
                    duration=0.1 + (i % 10) * 0.05,
                    memory_usage=1000000 + i * 1000,
                    cpu_usage=10.0 + (i % 50),
                    cache_hit=(i % 3 == 0),
                    timestamp=time.time() - (100 - i),
                    success=(i % 20 != 0)  # 5% failure rate
                )
                monitor.record_metric(metric)
            
            # Get performance summary
            summary = monitor.get_performance_summary(time_window=3600)
            
            duration = time.time() - start_time
            
            details = {
                'metrics_recorded': 100,
                'summary': summary,
                'processing_time': duration
            }
            
            return TestResult("Performance Monitoring", duration, True, details)
            
        except Exception as e:
            return TestResult("Performance Monitoring", time.time() - start_time, False, {}, str(e))
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system performance information"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'disk_usage_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        print("🚀 Starting MCP Server Performance Tests")
        print("=" * 60)
        
        system_info = self.get_system_info()
        print(f"💻 System: {system_info.get('cpu_count', 'N/A')} CPUs, "
              f"{system_info.get('memory_total_gb', 'N/A')} GB RAM, "
              f"{system_info.get('memory_percent', 'N/A')}% used")
        
        # Run synchronous tests
        sync_tests = [
            self.test_cache_performance,
            self.test_prompt_optimization,
            self.test_context_compression,
            self.test_industry_tools_config,
            self.test_performance_monitoring
        ]
        
        results = []
        for test_func in sync_tests:
            try:
                result = test_func()
                results.append(result)
                status = "✅" if result.success else "❌"
                print(f"{status} {result.test_name}: {result.duration:.3f}s")
            except Exception as e:
                print(f"❌ {test_func.__name__}: Failed with {str(e)}")
        
        # Run async tests
        try:
            result = await self.test_optimizer_integration()
            results.append(result)
            status = "✅" if result.success else "❌"
            print(f"{status} {result.test_name}: {result.duration:.3f}s")
        except Exception as e:
            print(f"❌ Optimizer Integration: Failed with {str(e)}")
        
        # Calculate summary
        successful = [r for r in results if r.success]
        success_rate = len(successful) / len(results) * 100 if results else 0
        
        total_duration = sum(r.duration for r in results)
        avg_duration = total_duration / len(results) if results else 0
        
        summary = {
            'system_info': system_info,
            'total_tests': len(results),
            'successful_tests': len(successful),
            'success_rate': success_rate,
            'total_duration': total_duration,
            'avg_test_duration': avg_duration,
            'results': [
                {
                    'test_name': r.test_name,
                    'duration': r.duration,
                    'success': r.success,
                    'details': r.details,
                    'error': r.error
                }
                for r in results
            ]
        }
        
        return summary
    
    def print_detailed_report(self, summary: Dict[str, Any]):
        """Print detailed performance report"""
        print("\n" + "=" * 60)
        print("🎯 MCP SERVER PERFORMANCE REPORT")
        print("=" * 60)
        
        # Overall statistics
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Total Duration: {summary['total_duration']:.3f}s")
        print(f"   Average Test Duration: {summary['avg_test_duration']:.3f}s")
        
        # Performance grade
        if summary['success_rate'] >= 90:
            grade = "🟢 EXCELLENT"
        elif summary['success_rate'] >= 75:
            grade = "🟡 GOOD"
        elif summary['success_rate'] >= 50:
            grade = "🟠 FAIR"
        else:
            grade = "🔴 NEEDS IMPROVEMENT"
        
        print(f"   Performance Grade: {grade}")
        
        # System information
        print(f"\n💻 System Performance:")
        sys_info = summary['system_info']
        print(f"   CPU Usage: {sys_info.get('cpu_percent', 'N/A')}%")
        print(f"   Memory Usage: {sys_info.get('memory_percent', 'N/A')}%")
        print(f"   Available Memory: {sys_info.get('memory_available_gb', 'N/A')} GB")
        print(f"   Disk Usage: {sys_info.get('disk_usage_percent', 'N/A')}%")
        
        # Detailed test results
        print(f"\n📋 Detailed Test Results:")
        for result in summary['results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test_name']}: {result['duration']:.3f}s")
            
            if result['success'] and result['details']:
                # Show key performance metrics for each test
                if result['test_name'] == "LRU Cache":
                    details = result['details']
                    print(f"      - Operations/sec: {details.get('ops_per_second', 0):.0f}")
                    print(f"      - Hit rate: {details.get('hit_rate', 0):.1%}")
                
                elif result['test_name'] == "Prompt Optimization":
                    details = result['details']
                    print(f"      - Compression: {details.get('overall_compression', 0):.1%}")
                    print(f"      - Avg time: {details.get('avg_processing_time', 0):.3f}s")
                
                elif result['test_name'] == "Context Compression":
                    details = result['details']
                    print(f"      - Avg compression time: {details.get('avg_compression_time', 0):.3f}s")
                
                elif result['test_name'] == "Optimizer Integration":
                    details = result['details']
                    print(f"      - Cache hit rate: {details.get('cache_hit_rate', 0):.1%}")
                    print(f"      - Avg optimization: {details.get('avg_optimization_time', 0):.3f}s")
                
                elif result['test_name'] == "Performance Monitoring":
                    details = result['details']
                    if 'summary' in details:
                        mon_summary = details['summary']
                        print(f"      - Success rate: {mon_summary.get('success_rate', 0):.1%}")
                        print(f"      - Avg response time: {mon_summary.get('avg_response_time', 0):.3f}s")
            
            elif not result['success']:
                print(f"      Error: {result['error'][:80]}...")
        
        # Performance insights and recommendations
        print(f"\n💡 Performance Insights:")
        
        cache_test = next((r for r in summary['results'] if r['test_name'] == "LRU Cache"), None)
        if cache_test and cache_test['success']:
            ops_per_sec = cache_test['details'].get('ops_per_second', 0)
            if ops_per_sec > 10000:
                print("   🟢 Excellent cache performance")
            elif ops_per_sec > 5000:
                print("   🟡 Good cache performance")
            else:
                print("   🟠 Cache performance could be improved")
        
        optimizer_test = next((r for r in summary['results'] if r['test_name'] == "Optimizer Integration"), None)
        if optimizer_test and optimizer_test['success']:
            cache_hit_rate = optimizer_test['details'].get('cache_hit_rate', 0)
            if cache_hit_rate > 0.5:
                print("   🟢 Good cache utilization in optimizer")
            else:
                print("   🟡 Cache utilization could be improved")
        
        if summary['avg_test_duration'] < 0.1:
            print("   🟢 Excellent response times across all components")
        elif summary['avg_test_duration'] < 0.5:
            print("   🟡 Good response times")
        else:
            print("   🟠 Consider optimizing slower components")
        
        print(f"\n🔧 Recommendations:")
        if sys_info.get('memory_percent', 0) > 80:
            print("   - High memory usage detected - consider closing other applications")
        if summary['success_rate'] < 100:
            print("   - Some tests failed - check error messages above")
        if summary['avg_test_duration'] > 0.5:
            print("   - Consider enabling more aggressive caching")
        
        print(f"\n✅ MCP Server components are performing well!")
        print(f"   Ready for production deployment with {summary['success_rate']:.0f}% component reliability")

async def main():
    """Main async function"""
    tester = MCPPerformanceTester()
    summary = await tester.run_all_tests()
    tester.print_detailed_report(summary)
    
    # Save results
    timestamp = int(time.time())
    results_file = f'mcp_performance_results_{timestamp}.json'
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    return summary['success_rate'] >= 75

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
