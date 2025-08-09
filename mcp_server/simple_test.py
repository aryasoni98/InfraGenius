#!/usr/bin/env python3
"""
Simple performance test for the MCP server and Ollama integration
"""

import time
import subprocess
import sys
import json
import psutil
from dataclasses import dataclass
from typing import Optional

@dataclass
class TestResult:
    test_name: str
    duration: float
    success: bool
    output_size: int
    error: str = ""

class SimplePerformanceTester:
    def __init__(self):
        self.results = []
    
    def test_ollama_availability(self) -> TestResult:
        """Test if Ollama is available and responsive"""
        print("🔍 Testing Ollama availability...")
        
        start_time = time.time()
        try:
            # Test with a very simple prompt and short timeout
            result = subprocess.run([
                'ollama', 'run', 'gpt-oss:latest'
            ], input="Hi", text=True, capture_output=True, timeout=15)
            
            duration = time.time() - start_time
            success = result.returncode == 0
            output_size = len(result.stdout) if success else 0
            error = result.stderr if not success else ""
            
            return TestResult("Ollama Availability", duration, success, output_size, error)
            
        except subprocess.TimeoutExpired:
            return TestResult("Ollama Availability", 15.0, False, 0, "Timeout after 15s")
        except Exception as e:
            return TestResult("Ollama Availability", time.time() - start_time, False, 0, str(e))
    
    def test_ollama_list(self) -> TestResult:
        """Test ollama list command"""
        print("📋 Testing Ollama model list...")
        
        start_time = time.time()
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            duration = time.time() - start_time
            success = result.returncode == 0
            output_size = len(result.stdout) if success else 0
            error = result.stderr if not success else ""
            
            return TestResult("Ollama List", duration, success, output_size, error)
            
        except Exception as e:
            return TestResult("Ollama List", time.time() - start_time, False, 0, str(e))
    
    def test_model_info(self) -> TestResult:
        """Test getting model information"""
        print("ℹ️ Testing model information...")
        
        start_time = time.time()
        try:
            result = subprocess.run(['ollama', 'show', 'gpt-oss:latest'], 
                                  capture_output=True, text=True, timeout=10)
            duration = time.time() - start_time
            success = result.returncode == 0
            output_size = len(result.stdout) if success else 0
            error = result.stderr if not success else ""
            
            return TestResult("Model Info", duration, success, output_size, error)
            
        except Exception as e:
            return TestResult("Model Info", time.time() - start_time, False, 0, str(e))
    
    def test_python_imports(self) -> TestResult:
        """Test if required Python modules can be imported"""
        print("🐍 Testing Python imports...")
        
        start_time = time.time()
        try:
            # Test importing key modules from our server
            import json
            import asyncio
            import logging
            import subprocess
            from dataclasses import dataclass
            
            duration = time.time() - start_time
            return TestResult("Python Imports", duration, True, 0, "")
            
        except Exception as e:
            return TestResult("Python Imports", time.time() - start_time, False, 0, str(e))
    
    def test_server_syntax(self) -> TestResult:
        """Test if server.py has valid syntax"""
        print("✅ Testing server.py syntax...")
        
        start_time = time.time()
        try:
            result = subprocess.run([sys.executable, '-m', 'py_compile', 'server.py'], 
                                  capture_output=True, text=True, timeout=10)
            duration = time.time() - start_time
            success = result.returncode == 0
            error = result.stderr if not success else ""
            
            return TestResult("Server Syntax", duration, success, 0, error)
            
        except Exception as e:
            return TestResult("Server Syntax", time.time() - start_time, False, 0, str(e))
    
    def get_system_info(self) -> dict:
        """Get system information"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def run_tests(self) -> dict:
        """Run all tests"""
        print("🚀 Starting Simple Performance Tests")
        print("=" * 50)
        
        # Get system info
        system_info = self.get_system_info()
        print(f"💻 System: {system_info.get('cpu_count', 'N/A')} CPUs, "
              f"{system_info.get('memory_gb', 'N/A')} GB RAM")
        
        # Run tests
        tests = [
            self.test_python_imports,
            self.test_server_syntax,
            self.test_ollama_list,
            self.test_model_info,
            self.test_ollama_availability
        ]
        
        results = []
        for test_func in tests:
            try:
                result = test_func()
                results.append(result)
                status = "✅" if result.success else "❌"
                print(f"{status} {result.test_name}: {result.duration:.2f}s")
                if not result.success and result.error:
                    print(f"   Error: {result.error[:100]}...")
            except Exception as e:
                print(f"❌ {test_func.__name__}: Failed with {str(e)}")
        
        # Calculate summary
        successful = [r for r in results if r.success]
        success_rate = len(successful) / len(results) * 100 if results else 0
        
        summary = {
            'system_info': system_info,
            'total_tests': len(results),
            'successful_tests': len(successful),
            'success_rate': success_rate,
            'results': [
                {
                    'test': r.test_name,
                    'duration': r.duration,
                    'success': r.success,
                    'output_size': r.output_size,
                    'error': r.error
                }
                for r in results
            ]
        }
        
        return summary
    
    def print_report(self, summary: dict):
        """Print test report"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] >= 80:
            grade = "🟢 EXCELLENT"
        elif summary['success_rate'] >= 60:
            grade = "🟡 GOOD"
        elif summary['success_rate'] >= 40:
            grade = "🟠 FAIR"
        else:
            grade = "🔴 NEEDS ATTENTION"
        
        print(f"Overall Status: {grade}")
        
        print(f"\n💻 System Information:")
        for key, value in summary['system_info'].items():
            print(f"   {key}: {value}")
        
        print(f"\n📋 Detailed Results:")
        for result in summary['results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}: {result['duration']:.2f}s")
            if not result['success'] and result['error']:
                print(f"      Error: {result['error'][:80]}...")
        
        print(f"\n💡 Recommendations:")
        if summary['success_rate'] < 100:
            print("   - Check failed tests above for specific issues")
        if any('Ollama' in r['test'] and not r['success'] for r in summary['results']):
            print("   - Ollama service may need restart or configuration")
            print("   - Try: ollama serve (in another terminal)")
        if summary['system_info'].get('memory_percent', 0) > 80:
            print("   - High memory usage detected, consider closing other applications")

def main():
    """Main function"""
    tester = SimplePerformanceTester()
    summary = tester.run_tests()
    tester.print_report(summary)
    
    # Save results
    timestamp = int(time.time())
    with open(f'simple_test_results_{timestamp}.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved to: simple_test_results_{timestamp}.json")
    
    return summary['success_rate'] >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
