#!/usr/bin/env python3
"""
Test MCP server startup and basic functionality
"""

import asyncio
import time
import json
import sys
from typing import Dict, Any
import subprocess
import signal
import os

class ServerTester:
    """Test MCP server startup and basic operations"""
    
    def __init__(self):
        self.server_process = None
        
    async def test_server_import(self) -> Dict[str, Any]:
        """Test if server can be imported and initialized"""
        print("📦 Testing server module import...")
        
        start_time = time.time()
        try:
            # Import the server module
            import server
            
            # Try to create server instance (without running it)
            server_instance = server.DevOpsMCPServer()
            
            duration = time.time() - start_time
            
            return {
                'test': 'Server Import',
                'success': True,
                'duration': duration,
                'details': {
                    'server_class': str(type(server_instance)),
                    'model': server_instance.model,
                    'context': str(server_instance.context),
                    'prompts_loaded': len(server_instance.prompts) if hasattr(server_instance, 'prompts') else 0
                }
            }
            
        except Exception as e:
            return {
                'test': 'Server Import',
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_server_tools(self) -> Dict[str, Any]:
        """Test server tools registration"""
        print("🛠️ Testing server tools...")
        
        start_time = time.time()
        try:
            import server
            server_instance = server.DevOpsMCPServer()
            
            # Check if tools are registered (they should be decorated methods)
            tools_count = 0
            for attr_name in dir(server_instance):
                if not attr_name.startswith('_'):
                    attr = getattr(server_instance, attr_name)
                    if callable(attr) and hasattr(attr, '__name__'):
                        if any(name in attr.__name__ for name in ['analyze', 'audit', 'plan', 'assess']):
                            tools_count += 1
            
            duration = time.time() - start_time
            
            return {
                'test': 'Server Tools',
                'success': True,
                'duration': duration,
                'details': {
                    'estimated_tools': tools_count,
                    'server_methods': len([m for m in dir(server_instance) if not m.startswith('_')])
                }
            }
            
        except Exception as e:
            return {
                'test': 'Server Tools',
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_performance_components(self) -> Dict[str, Any]:
        """Test performance optimization components"""
        print("⚡ Testing performance components...")
        
        start_time = time.time()
        try:
            from performance_optimizer import CursorAIOptimizer
            
            optimizer = CursorAIOptimizer()
            
            # Test optimization request
            result = await optimizer.optimize_request(
                prompt="Test DevOps analysis",
                context="Test context for performance measurement",
                domain="devops"
            )
            
            # Get performance stats
            stats = optimizer.get_performance_stats()
            
            duration = time.time() - start_time
            
            return {
                'test': 'Performance Components',
                'success': True,
                'duration': duration,
                'details': {
                    'optimization_result': bool(result),
                    'cache_hit': result.get('cache_hit', False),
                    'processing_time': result.get('processing_time', 0),
                    'performance_stats': stats
                }
            }
            
        except Exception as e:
            return {
                'test': 'Performance Components',
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_mock_analysis(self) -> Dict[str, Any]:
        """Test mock analysis without Ollama"""
        print("🧪 Testing mock analysis...")
        
        start_time = time.time()
        try:
            import server
            from performance_optimizer import AnalysisResult
            
            server_instance = server.DevOpsMCPServer()
            
            # Create a mock analysis result
            mock_result = AnalysisResult(
                analysis_id="test-123",
                timestamp=str(time.time()),
                category="devops",
                severity="medium",
                confidence=0.85,
                findings=["Mock finding 1", "Mock finding 2"],
                recommendations=["Mock recommendation 1", "Mock recommendation 2"],
                metrics={"processing_time": 0.1, "accuracy": 0.9}
            )
            
            # Test result parsing
            result_dict = server_instance.parse_analysis_result(
                json.dumps(mock_result.__dict__), 
                "devops"
            )
            
            duration = time.time() - start_time
            
            return {
                'test': 'Mock Analysis',
                'success': True,
                'duration': duration,
                'details': {
                    'analysis_id': result_dict.analysis_id,
                    'category': result_dict.category,
                    'confidence': result_dict.confidence,
                    'findings_count': len(result_dict.findings),
                    'recommendations_count': len(result_dict.recommendations)
                }
            }
            
        except Exception as e:
            return {
                'test': 'Mock Analysis',
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def test_configuration_loading(self) -> Dict[str, Any]:
        """Test configuration file loading"""
        print("⚙️ Testing configuration loading...")
        
        start_time = time.time()
        try:
            # Load and validate configuration
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = ['server', 'ollama', 'domains', 'performance']
            missing_sections = [section for section in required_sections if section not in config]
            
            # Check domain configurations
            domains = config.get('domains', {})
            enabled_domains = [domain for domain, conf in domains.items() if conf.get('enabled', False)]
            
            duration = time.time() - start_time
            
            return {
                'test': 'Configuration Loading',
                'success': len(missing_sections) == 0,
                'duration': duration,
                'details': {
                    'config_size': len(json.dumps(config)),
                    'missing_sections': missing_sections,
                    'enabled_domains': enabled_domains,
                    'total_domains': len(domains),
                    'server_name': config.get('server', {}).get('name', 'Unknown')
                }
            }
            
        except Exception as e:
            return {
                'test': 'Configuration Loading',
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive server tests"""
        print("🚀 Starting MCP Server Startup Tests")
        print("=" * 60)
        
        tests = [
            self.test_configuration_loading,
            self.test_server_import,
            self.test_server_tools,
            self.test_performance_components,
            self.test_mock_analysis
        ]
        
        results = []
        total_duration = 0
        
        for test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                status = "✅" if result['success'] else "❌"
                print(f"{status} {result['test']}: {result['duration']:.3f}s")
                total_duration += result['duration']
                
                if not result['success'] and 'error' in result:
                    print(f"   Error: {result['error'][:100]}...")
                    
            except Exception as e:
                print(f"❌ {test_func.__name__}: Failed with {str(e)}")
                results.append({
                    'test': test_func.__name__,
                    'success': False,
                    'duration': 0,
                    'error': str(e)
                })
        
        # Calculate summary
        successful = [r for r in results if r['success']]
        success_rate = len(successful) / len(results) * 100 if results else 0
        
        summary = {
            'total_tests': len(results),
            'successful_tests': len(successful),
            'success_rate': success_rate,
            'total_duration': total_duration,
            'avg_duration': total_duration / len(results) if results else 0,
            'results': results
        }
        
        return summary
    
    def print_summary_report(self, summary: Dict[str, Any]):
        """Print test summary report"""
        print("\n" + "=" * 60)
        print("🎯 MCP SERVER STARTUP TEST SUMMARY")
        print("=" * 60)
        
        print(f"📊 Test Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Total Duration: {summary['total_duration']:.3f}s")
        print(f"   Average Duration: {summary['avg_duration']:.3f}s")
        
        # Grade the results
        if summary['success_rate'] >= 90:
            grade = "🟢 EXCELLENT - Ready for deployment"
        elif summary['success_rate'] >= 75:
            grade = "🟡 GOOD - Minor issues to resolve"
        elif summary['success_rate'] >= 50:
            grade = "🟠 FAIR - Several issues need attention"
        else:
            grade = "🔴 POOR - Major issues prevent deployment"
        
        print(f"   Overall Grade: {grade}")
        
        # Show detailed results
        print(f"\n📋 Detailed Results:")
        for result in summary['results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}: {result['duration']:.3f}s")
            
            if result['success'] and 'details' in result:
                details = result['details']
                if result['test'] == 'Configuration Loading':
                    print(f"      - Enabled domains: {len(details.get('enabled_domains', []))}")
                    print(f"      - Server: {details.get('server_name', 'N/A')}")
                elif result['test'] == 'Server Import':
                    print(f"      - Model: {details.get('model', 'N/A')}")
                    print(f"      - Prompts: {details.get('prompts_loaded', 0)}")
                elif result['test'] == 'Performance Components':
                    print(f"      - Processing time: {details.get('processing_time', 0):.3f}s")
                    print(f"      - Cache hit: {details.get('cache_hit', False)}")
                elif result['test'] == 'Mock Analysis':
                    print(f"      - Confidence: {details.get('confidence', 0):.1%}")
                    print(f"      - Findings: {details.get('findings_count', 0)}")
            
            elif not result['success']:
                print(f"      Error: {result.get('error', 'Unknown error')[:80]}...")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if summary['success_rate'] == 100:
            print("   🎉 All tests passed! MCP server is ready for deployment.")
            print("   🚀 You can now start the server with: python server.py")
        else:
            print("   🔍 Review failed tests above and resolve issues")
            if any('Import' in r['test'] and not r['success'] for r in summary['results']):
                print("   📦 Check Python dependencies and module imports")
            if any('Configuration' in r['test'] and not r['success'] for r in summary['results']):
                print("   ⚙️ Verify config.json file is valid and complete")
        
        print(f"\n✅ Server components test completed!")
        print(f"   Readiness Score: {summary['success_rate']:.0f}%")

async def main():
    """Main function"""
    tester = ServerTester()
    summary = await tester.run_comprehensive_test()
    tester.print_summary_report(summary)
    
    # Save results
    timestamp = int(time.time())
    results_file = f'server_startup_test_{timestamp}.json'
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    return summary['success_rate'] >= 80

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
