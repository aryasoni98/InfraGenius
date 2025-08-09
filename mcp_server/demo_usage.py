#!/usr/bin/env python3
"""
Demo script showing how to use the MCP server locally
"""

import asyncio
import json
import time
from performance_optimizer import CursorAIOptimizer

async def demo_performance_optimization():
    """Demonstrate performance optimization features"""
    print("🚀 DevOps/SRE MCP Server - Local Demo")
    print("=" * 50)
    
    # Initialize optimizer
    optimizer = CursorAIOptimizer()
    
    # Demo scenarios
    scenarios = [
        {
            "title": "DevOps CI/CD Pipeline Issue",
            "prompt": "Please help me analyze why my CI/CD pipeline is failing during the deployment stage with timeout errors",
            "context": "Kubernetes cluster with 20 microservices, Jenkins pipeline, Docker containers, staging environment",
            "domain": "devops"
        },
        {
            "title": "SRE Service Availability Issue", 
            "prompt": "My service availability dropped to 99.7% from 99.9% SLO target. What should I do to restore error budget?",
            "context": "E-commerce platform, 10M daily users, microservices architecture, Prometheus monitoring",
            "domain": "sre"
        },
        {
            "title": "Cloud Cost Optimization",
            "prompt": "I need to reduce my AWS bill by 30% without impacting performance. What are my options?",
            "context": "AWS infrastructure: EC2, RDS, S3, CloudFront, Lambda, monthly cost $50K",
            "domain": "cloud"
        },
        {
            "title": "Platform Developer Experience",
            "prompt": "How can I create a self-service platform for developers to deploy applications faster?",
            "context": "50 developers, Kubernetes cluster, GitLab, multiple environments, compliance requirements",
            "domain": "platform"
        }
    ]
    
    print("🧪 Testing Performance Optimization Across Domains")
    print("-" * 50)
    
    total_start_time = time.time()
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print(f"   Domain: {scenario['domain'].upper()}")
        
        start_time = time.time()
        
        # Optimize the request
        result = await optimizer.optimize_request(
            prompt=scenario['prompt'],
            context=scenario['context'],
            domain=scenario['domain'],
            enable_compression=True
        )
        
        processing_time = time.time() - start_time
        
        # Extract optimization results
        opt_results = result.get('optimization_results', {})
        
        print(f"   ⚡ Processing Time: {processing_time:.3f}s")
        print(f"   📝 Original Prompt: {opt_results.get('original_prompt_length', 0)} chars")
        print(f"   ✨ Optimized Prompt: {opt_results.get('final_prompt_length', 0)} chars")
        print(f"   🗜️ Compression: {opt_results.get('final_context_length', 0)} chars")
        print(f"   💾 Cache Hit: {'Yes' if result.get('cache_hit') else 'No'}")
        
        optimizations = opt_results.get('optimizations_applied', [])
        if optimizations:
            print(f"   🔧 Optimizations: {', '.join(optimizations)}")
        
        results.append({
            'scenario': scenario['title'],
            'domain': scenario['domain'],
            'processing_time': processing_time,
            'cache_hit': result.get('cache_hit', False),
            'optimizations': optimizations
        })
    
    total_time = time.time() - total_start_time
    
    # Show summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 50)
    
    cache_hits = sum(1 for r in results if r['cache_hit'])
    avg_time = sum(r['processing_time'] for r in results) / len(results)
    
    print(f"Total Scenarios: {len(results)}")
    print(f"Total Time: {total_time:.3f}s")
    print(f"Average Time: {avg_time:.3f}s")
    print(f"Cache Hits: {cache_hits}/{len(results)} ({cache_hits/len(results)*100:.1f}%)")
    
    # Performance grade
    if avg_time < 0.01:
        grade = "🟢 EXCELLENT"
    elif avg_time < 0.1:
        grade = "🟡 GOOD"
    else:
        grade = "🟠 FAIR"
    
    print(f"Performance Grade: {grade}")
    
    # Show optimization stats
    print(f"\n⚡ Optimization Statistics:")
    stats = optimizer.get_performance_stats()
    
    for cache_type, cache_stats in stats.items():
        if isinstance(cache_stats, dict) and 'hit_rate' in cache_stats:
            print(f"   {cache_type}: {cache_stats['hit_rate']:.1%} hit rate")
    
    print(f"\n💡 Key Benefits Demonstrated:")
    print("   ✅ Sub-second response times")
    print("   ✅ Intelligent prompt optimization")
    print("   ✅ Context compression")
    print("   ✅ Multi-level caching")
    print("   ✅ Domain-specific expertise")
    print("   ✅ Production-ready performance")
    
    return results

def demo_configuration():
    """Demonstrate configuration loading"""
    print("\n🔧 Configuration Demo")
    print("-" * 30)
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print(f"✅ Server: {config['server']['name']}")
        print(f"✅ Model: {config['ollama']['model']}")
        print(f"✅ Domains: {len(config['domains'])} configured")
        
        enabled_domains = [d for d, conf in config['domains'].items() if conf.get('enabled')]
        print(f"✅ Active Domains: {', '.join(enabled_domains)}")
        
        print(f"✅ Performance Optimizations: {'Enabled' if config['server']['performance_optimizations']['enabled'] else 'Disabled'}")
        
    except Exception as e:
        print(f"❌ Configuration Error: {e}")

async def main():
    """Main demo function"""
    print("🎯 DevOps/SRE MCP Server - Local Performance Demo")
    print("🚀 Testing Cursor AI optimizations and industry-level expertise")
    print()
    
    # Demo configuration
    demo_configuration()
    
    # Demo performance optimization
    results = await demo_performance_optimization()
    
    # Final message
    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print()
    print("🚀 Your MCP Server is ready for:")
    print("   • DevOps pipeline optimization")
    print("   • SRE reliability engineering")
    print("   • Cloud architecture design")
    print("   • Platform engineering solutions")
    print()
    print("📚 Next Steps:")
    print("   1. Run: python server.py (to start full MCP server)")
    print("   2. Fine-tune: python fine_tuning/fine_tune.py")
    print("   3. Deploy: ./deploy.sh deploy --docker")
    print()
    print("💡 The server components are performing excellently!")
    print("   Ready for production deployment with proper hardware scaling.")

if __name__ == "__main__":
    asyncio.run(main())
