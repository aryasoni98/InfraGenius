#!/usr/bin/env python3
"""
Performance testing script for DevOps/SRE MCP Server
Tests various scenarios and measures response times, accuracy, and resource usage
"""

import asyncio
import json
import time
import psutil
import statistics
from typing import Dict, List, Any
import subprocess
import requests
import threading
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import sys
import os

@dataclass
class PerformanceResult:
    """Performance test result"""
    test_name: str
    response_time: float
    success: bool
    response_size: int
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_hit: bool = False
    error_message: str = ""

class PerformanceTester:
    """Comprehensive performance testing for the MCP server"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.results = []
        self.process = psutil.Process()
        
    def measure_system_resources(self) -> Dict[str, float]:
        """Measure current system resource usage"""
        return {
            'memory_mb': self.process.memory_info().rss / 1024 / 1024,
            'cpu_percent': self.process.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent
        }
    
    def test_ollama_direct(self) -> PerformanceResult:
        """Test direct Ollama performance"""
        print("🧪 Testing direct Ollama performance...")
        
        test_prompt = "Analyze this DevOps scenario: CI/CD pipeline failed during deployment stage. Provide recommendations."
        
        start_time = time.time()
        start_resources = self.measure_system_resources()
        
        try:
            # Test with gpt-oss:latest
            process = subprocess.run([
                'ollama', 'run', 'gpt-oss:latest'
            ], input=test_prompt, text=True, capture_output=True, timeout=60)
            
            end_time = time.time()
            end_resources = self.measure_system_resources()
            
            response_time = end_time - start_time
            success = process.returncode == 0
            response_size = len(process.stdout) if success else 0
            
            return PerformanceResult(
                test_name="Direct Ollama",
                response_time=response_time,
                success=success,
                response_size=response_size,
                memory_usage_mb=end_resources['memory_mb'] - start_resources['memory_mb'],
                cpu_usage_percent=end_resources['cpu_percent'],
                error_message=process.stderr if not success else ""
            )
            
        except subprocess.TimeoutExpired:
            return PerformanceResult(
                test_name="Direct Ollama",
                response_time=60.0,
                success=False,
                response_size=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                error_message="Timeout after 60 seconds"
            )
        except Exception as e:
            return PerformanceResult(
                test_name="Direct Ollama",
                response_time=time.time() - start_time,
                success=False,
                response_size=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                error_message=str(e)
            )
    
    def test_mcp_server_health(self) -> PerformanceResult:
        """Test MCP server health endpoint"""
        print("🏥 Testing MCP server health endpoint...")
        
        start_time = time.time()
        start_resources = self.measure_system_resources()
        
        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            end_time = time.time()
            end_resources = self.measure_system_resources()
            
            return PerformanceResult(
                test_name="Health Check",
                response_time=end_time - start_time,
                success=response.status_code == 200,
                response_size=len(response.text),
                memory_usage_mb=end_resources['memory_mb'] - start_resources['memory_mb'],
                cpu_usage_percent=end_resources['cpu_percent'],
                error_message="" if response.status_code == 200 else f"HTTP {response.status_code}"
            )
            
        except Exception as e:
            return PerformanceResult(
                test_name="Health Check",
                response_time=time.time() - start_time,
                success=False,
                response_size=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                error_message=str(e)
            )
    
    def test_log_analysis(self) -> PerformanceResult:
        """Test log analysis performance"""
        print("📊 Testing log analysis performance...")
        
        test_logs = """
2024-01-15T10:30:15Z [ERROR] api-gateway: High response time detected - 2.5s average
2024-01-15T10:30:16Z [ERROR] database-service: Connection pool exhausted - 100/100 connections in use
2024-01-15T10:30:17Z [WARN] load-balancer: Health check failures increasing
2024-01-15T10:30:18Z [INFO] auto-scaler: Scaling up due to high CPU utilization
        """
        
        start_time = time.time()
        start_resources = self.measure_system_resources()
        
        try:
            # Simulate MCP tool call (since we don't have the actual MCP client)
            # This would normally be done through the MCP protocol
            payload = {
                "tool": "analyze_logs",
                "parameters": {
                    "logs": test_logs,
                    "analysis_type": "devops",
                    "context": "Production Kubernetes cluster"
                }
            }
            
            # For now, test the Ollama integration directly
            prompt = f"""
You are a Senior DevOps Engineer. Analyze these logs and provide recommendations:

{test_logs}

Context: Production Kubernetes cluster
Analysis Type: DevOps

Provide structured analysis with:
1. Root cause analysis
2. Impact assessment  
3. Immediate actions
4. Long-term recommendations
"""
            
            process = subprocess.run([
                'ollama', 'run', 'gpt-oss:latest', 
                '--temperature', '0.1'
            ], input=prompt, text=True, capture_output=True, timeout=120)
            
            end_time = time.time()
            end_resources = self.measure_system_resources()
            
            return PerformanceResult(
                test_name="Log Analysis",
                response_time=end_time - start_time,
                success=process.returncode == 0,
                response_size=len(process.stdout) if process.returncode == 0 else 0,
                memory_usage_mb=end_resources['memory_mb'] - start_resources['memory_mb'],
                cpu_usage_percent=end_resources['cpu_percent'],
                error_message=process.stderr if process.returncode != 0 else ""
            )
            
        except Exception as e:
            return PerformanceResult(
                test_name="Log Analysis",
                response_time=time.time() - start_time,
                success=False,
                response_size=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                error_message=str(e)
            )
    
    def test_concurrent_requests(self, num_requests: int = 5) -> List[PerformanceResult]:
        """Test concurrent request handling"""
        print(f"🚀 Testing {num_requests} concurrent requests...")
        
        def single_request(request_id: int) -> PerformanceResult:
            test_prompt = f"Request {request_id}: Explain Kubernetes pod scheduling and resource allocation."
            
            start_time = time.time()
            start_resources = self.measure_system_resources()
            
            try:
                process = subprocess.run([
                    'ollama', 'run', 'gpt-oss:latest',
                    '--temperature', '0.1'
                ], input=test_prompt, text=True, capture_output=True, timeout=90)
                
                end_time = time.time()
                end_resources = self.measure_system_resources()
                
                return PerformanceResult(
                    test_name=f"Concurrent Request {request_id}",
                    response_time=end_time - start_time,
                    success=process.returncode == 0,
                    response_size=len(process.stdout) if process.returncode == 0 else 0,
                    memory_usage_mb=end_resources['memory_mb'] - start_resources['memory_mb'],
                    cpu_usage_percent=end_resources['cpu_percent'],
                    error_message=process.stderr if process.returncode != 0 else ""
                )
                
            except Exception as e:
                return PerformanceResult(
                    test_name=f"Concurrent Request {request_id}",
                    response_time=time.time() - start_time,
                    success=False,
                    response_size=0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0,
                    error_message=str(e)
                )
        
        # Run concurrent requests
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(single_request, i) for i in range(num_requests)]
            results = [future.result() for future in futures]
        
        return results
    
    def test_different_domains(self) -> List[PerformanceResult]:
        """Test performance across different domains"""
        print("🎯 Testing performance across different domains...")
        
        domain_tests = [
            {
                "domain": "DevOps",
                "prompt": "Design a CI/CD pipeline for a microservices application with security scanning and automated testing."
            },
            {
                "domain": "SRE", 
                "prompt": "My service has a 99.9% availability SLO but is currently at 99.7%. What actions should I take to restore the error budget?"
            },
            {
                "domain": "Cloud",
                "prompt": "Design a cost-effective, scalable architecture for a high-traffic web application on AWS with disaster recovery."
            },
            {
                "domain": "Platform",
                "prompt": "How do I create a self-service platform for developers to deploy microservices with proper governance?"
            }
        ]
        
        results = []
        
        for test in domain_tests:
            print(f"  Testing {test['domain']} domain...")
            
            start_time = time.time()
            start_resources = self.measure_system_resources()
            
            try:
                enhanced_prompt = f"""
You are a {test['domain']} expert with industry-level expertise. 

{test['prompt']}

Provide a comprehensive, structured response with:
1. Analysis of requirements
2. Detailed solution architecture
3. Implementation steps
4. Best practices and security considerations
5. Monitoring and maintenance recommendations
"""
                
                process = subprocess.run([
                    'ollama', 'run', 'gpt-oss:latest',
                    '--temperature', '0.1'
                ], input=enhanced_prompt, text=True, capture_output=True, timeout=120)
                
                end_time = time.time()
                end_resources = self.measure_system_resources()
                
                result = PerformanceResult(
                    test_name=f"{test['domain']} Domain",
                    response_time=end_time - start_time,
                    success=process.returncode == 0,
                    response_size=len(process.stdout) if process.returncode == 0 else 0,
                    memory_usage_mb=end_resources['memory_mb'] - start_resources['memory_mb'],
                    cpu_usage_percent=end_resources['cpu_percent'],
                    error_message=process.stderr if process.returncode != 0 else ""
                )
                
                results.append(result)
                
            except Exception as e:
                result = PerformanceResult(
                    test_name=f"{test['domain']} Domain",
                    response_time=time.time() - start_time,
                    success=False,
                    response_size=0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0,
                    error_message=str(e)
                )
                results.append(result)
        
        return results
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        print("🚀 Starting Comprehensive Performance Tests")
        print("=" * 60)
        
        all_results = []
        
        # Test 1: Direct Ollama performance
        result = self.test_ollama_direct()
        all_results.append(result)
        print(f"✅ Direct Ollama: {result.response_time:.2f}s - {'Success' if result.success else 'Failed'}")
        
        # Test 2: Health check (if server is running)
        result = self.test_mcp_server_health()
        all_results.append(result)
        print(f"✅ Health Check: {result.response_time:.2f}s - {'Success' if result.success else 'Failed'}")
        
        # Test 3: Log analysis
        result = self.test_log_analysis()
        all_results.append(result)
        print(f"✅ Log Analysis: {result.response_time:.2f}s - {'Success' if result.success else 'Failed'}")
        
        # Test 4: Domain-specific tests
        domain_results = self.test_different_domains()
        all_results.extend(domain_results)
        for result in domain_results:
            print(f"✅ {result.test_name}: {result.response_time:.2f}s - {'Success' if result.success else 'Failed'}")
        
        # Test 5: Concurrent requests (smaller batch for testing)
        concurrent_results = self.test_concurrent_requests(num_requests=3)
        all_results.extend(concurrent_results)
        avg_concurrent_time = statistics.mean([r.response_time for r in concurrent_results if r.success])
        print(f"✅ Concurrent Requests (3): Avg {avg_concurrent_time:.2f}s")
        
        # Calculate summary statistics
        successful_results = [r for r in all_results if r.success]
        
        if successful_results:
            response_times = [r.response_time for r in successful_results]
            response_sizes = [r.response_size for r in successful_results]
            
            summary = {
                'total_tests': len(all_results),
                'successful_tests': len(successful_results),
                'success_rate': len(successful_results) / len(all_results) * 100,
                'avg_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'p95_response_time': sorted(response_times)[int(0.95 * len(response_times))],
                'avg_response_size': statistics.mean(response_sizes),
                'total_response_size': sum(response_sizes),
                'system_resources': self.measure_system_resources(),
                'detailed_results': [asdict(r) for r in all_results]
            }
        else:
            summary = {
                'total_tests': len(all_results),
                'successful_tests': 0,
                'success_rate': 0,
                'error': 'No successful tests',
                'detailed_results': [asdict(r) for r in all_results]
            }
        
        return summary
    
    def print_performance_report(self, summary: Dict[str, Any]) -> None:
        """Print detailed performance report"""
        print("\n" + "=" * 60)
        print("🎯 PERFORMANCE TEST RESULTS")
        print("=" * 60)
        
        if summary['successful_tests'] > 0:
            print(f"📊 Overall Performance:")
            print(f"   Total Tests: {summary['total_tests']}")
            print(f"   Successful: {summary['successful_tests']}")
            print(f"   Success Rate: {summary['success_rate']:.1f}%")
            print(f"   Average Response Time: {summary['avg_response_time']:.2f}s")
            print(f"   Median Response Time: {summary['median_response_time']:.2f}s")
            print(f"   P95 Response Time: {summary['p95_response_time']:.2f}s")
            print(f"   Min Response Time: {summary['min_response_time']:.2f}s")
            print(f"   Max Response Time: {summary['max_response_time']:.2f}s")
            
            print(f"\n📈 Response Analysis:")
            print(f"   Average Response Size: {summary['avg_response_size']:.0f} chars")
            print(f"   Total Data Processed: {summary['total_response_size']:.0f} chars")
            
            print(f"\n💻 System Resources:")
            resources = summary['system_resources']
            print(f"   Memory Usage: {resources['memory_mb']:.1f} MB")
            print(f"   CPU Usage: {resources['cpu_percent']:.1f}%")
            print(f"   System Memory: {resources['memory_percent']:.1f}%")
            print(f"   Disk Usage: {resources['disk_usage_percent']:.1f}%")
            
            # Performance grades
            avg_time = summary['avg_response_time']
            if avg_time < 2:
                grade = "🟢 EXCELLENT"
            elif avg_time < 5:
                grade = "🟡 GOOD"
            elif avg_time < 10:
                grade = "🟠 FAIR"
            else:
                grade = "🔴 NEEDS IMPROVEMENT"
            
            print(f"\n🏆 Performance Grade: {grade}")
            
            # Recommendations
            print(f"\n💡 Recommendations:")
            if avg_time > 5:
                print("   - Consider enabling caching for frequently used prompts")
                print("   - Optimize prompt length and complexity")
                print("   - Consider using a smaller model for simple queries")
            if summary['success_rate'] < 100:
                print("   - Investigate failed tests for reliability improvements")
                print("   - Implement retry logic for transient failures")
            if resources['memory_percent'] > 80:
                print("   - Monitor memory usage and consider scaling")
            
        else:
            print("❌ No successful tests completed")
            print("🔍 Check the detailed results below for error information")
        
        print(f"\n📋 Detailed Results:")
        for result in summary['detailed_results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test_name']}: {result['response_time']:.2f}s")
            if not result['success'] and result['error_message']:
                print(f"      Error: {result['error_message']}")

def main():
    """Main execution function"""
    print("🚀 DevOps/SRE MCP Server Performance Testing")
    print("=" * 60)
    
    # Initialize tester
    tester = PerformanceTester()
    
    # Run comprehensive tests
    summary = tester.run_comprehensive_tests()
    
    # Print detailed report
    tester.print_performance_report(summary)
    
    # Save results to file
    timestamp = int(time.time())
    results_file = f"performance_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    print("\n🎉 Performance testing completed!")
    
    return summary['success_rate'] > 50  # Return success if >50% tests passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
