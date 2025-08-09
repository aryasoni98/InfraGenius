#!/usr/bin/env python3
"""
Cost Calculator and Business Model for DevOps/SRE MCP Server
Calculates infrastructure costs, pricing strategy, and revenue projections
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"

class Region(Enum):
    US_EAST_1 = "us-east-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"

@dataclass
class InfrastructureCost:
    compute: float
    gpu: float
    storage: float
    network: float
    database: float
    cache: float
    load_balancer: float
    monitoring: float
    security: float
    backup: float
    total: float

@dataclass
class OperationalCost:
    staff: float
    support: float
    marketing: float
    legal: float
    office: float
    tools: float
    total: float

@dataclass
class RevenueProjection:
    free_users: int
    starter_users: int
    professional_users: int
    enterprise_users: int
    custom_users: int
    monthly_revenue: float
    annual_revenue: float

class CostCalculator:
    """Calculate infrastructure and operational costs"""
    
    # Pricing data (per month in USD)
    CLOUD_PRICING = {
        CloudProvider.AWS: {
            'compute_per_vcpu': 25.0,  # t3.medium equivalent
            'gpu_per_hour': 0.526,     # g4dn.xlarge
            'storage_per_gb': 0.10,    # EBS gp2
            'network_per_gb': 0.09,    # Data transfer out
            'database_per_hour': 0.068, # db.t3.micro
            'cache_per_hour': 0.017,   # cache.t3.micro
            'load_balancer': 25.0,     # Application LB
            'monitoring': 30.0,        # CloudWatch
            'security': 20.0,          # WAF, Secrets Manager
            'backup_per_gb': 0.05      # S3 backup
        },
        CloudProvider.GCP: {
            'compute_per_vcpu': 24.0,  # n1-standard-2 equivalent
            'gpu_per_hour': 0.45,      # T4 GPU
            'storage_per_gb': 0.04,    # Persistent disk
            'network_per_gb': 0.08,    # Egress pricing
            'database_per_hour': 0.065, # Cloud SQL
            'cache_per_hour': 0.049,   # Memorystore
            'load_balancer': 20.0,     # HTTP(S) LB
            'monitoring': 25.0,        # Cloud Monitoring
            'security': 15.0,          # Cloud Security
            'backup_per_gb': 0.026     # Cloud Storage
        },
        CloudProvider.AZURE: {
            'compute_per_vcpu': 26.0,  # Standard_D2s_v3
            'gpu_per_hour': 0.90,      # NC4as_T4_v3
            'storage_per_gb': 0.045,   # Premium SSD
            'network_per_gb': 0.087,   # Bandwidth
            'database_per_hour': 0.073, # Azure Database
            'cache_per_hour': 0.027,   # Redis Cache
            'load_balancer': 25.0,     # Standard LB
            'monitoring': 30.0,        # Azure Monitor
            'security': 18.0,          # Security Center
            'backup_per_gb': 0.05      # Blob Storage
        }
    }
    
    # Regional multipliers
    REGIONAL_MULTIPLIERS = {
        Region.US_EAST_1: 1.0,
        Region.US_WEST_2: 1.05,
        Region.EU_WEST_1: 1.15,
        Region.AP_SOUTHEAST_1: 1.20
    }
    
    def __init__(self):
        self.hours_per_month = 24 * 30  # 720 hours
        
    def calculate_infrastructure_cost(
        self,
        provider: CloudProvider,
        region: Region,
        compute_vcpus: int = 6,
        gpu_instances: int = 2,
        storage_gb: int = 500,
        network_gb_per_month: int = 1000,
        enable_ha: bool = True,
        environment: str = "production"
    ) -> InfrastructureCost:
        """Calculate infrastructure costs for a given configuration"""
        
        pricing = self.CLOUD_PRICING[provider]
        multiplier = self.REGIONAL_MULTIPLIERS[region]
        
        # Base costs
        compute = compute_vcpus * pricing['compute_per_vcpu'] * multiplier
        gpu = gpu_instances * pricing['gpu_per_hour'] * self.hours_per_month * multiplier
        storage = storage_gb * pricing['storage_per_gb'] * multiplier
        network = network_gb_per_month * pricing['network_per_gb'] * multiplier
        database = pricing['database_per_hour'] * self.hours_per_month * multiplier
        cache = pricing['cache_per_hour'] * self.hours_per_month * multiplier
        load_balancer = pricing['load_balancer'] * multiplier
        monitoring = pricing['monitoring'] * multiplier
        security = pricing['security'] * multiplier
        backup = (storage_gb * 0.3) * pricing['backup_per_gb'] * multiplier  # 30% of storage for backups
        
        # High availability multiplier
        if enable_ha:
            compute *= 1.5
            database *= 2  # Multi-AZ
            cache *= 1.5
            load_balancer *= 1.2
        
        # Environment adjustments
        if environment == "development":
            # Dev environments are typically smaller
            compute *= 0.5
            gpu *= 0.5
            storage *= 0.3
            database *= 0.5
            cache *= 0.5
        
        total = compute + gpu + storage + network + database + cache + load_balancer + monitoring + security + backup
        
        return InfrastructureCost(
            compute=round(compute, 2),
            gpu=round(gpu, 2),
            storage=round(storage, 2),
            network=round(network, 2),
            database=round(database, 2),
            cache=round(cache, 2),
            load_balancer=round(load_balancer, 2),
            monitoring=round(monitoring, 2),
            security=round(security, 2),
            backup=round(backup, 2),
            total=round(total, 2)
        )
    
    def calculate_operational_cost(
        self,
        team_size: int = 2,
        support_tier: str = "basic",
        marketing_budget: int = 5000,
        include_office: bool = False
    ) -> OperationalCost:
        """Calculate monthly operational costs"""
        
        # Staff costs (per month)
        avg_devops_salary = 12000  # $144k annually
        staff = team_size * avg_devops_salary
        
        # Support costs
        support_costs = {
            "basic": 2000,    # Basic support tools
            "premium": 5000,  # Premium support + tools
            "enterprise": 10000  # Dedicated support team
        }
        support = support_costs.get(support_tier, 2000)
        
        # Marketing
        marketing = marketing_budget
        
        # Legal and compliance
        legal = 2000
        
        # Office costs (if applicable)
        office = 3000 if include_office else 0
        
        # Tools and software
        tools = 1500  # Development tools, monitoring, etc.
        
        total = staff + support + marketing + legal + office + tools
        
        return OperationalCost(
            staff=staff,
            support=support,
            marketing=marketing,
            legal=legal,
            office=office,
            tools=tools,
            total=total
        )
    
    def calculate_multi_cloud_cost(
        self,
        regions: List[Tuple[CloudProvider, Region]],
        traffic_split: Optional[Dict[str, float]] = None
    ) -> Dict[str, InfrastructureCost]:
        """Calculate costs for multi-cloud deployment"""
        
        if traffic_split is None:
            # Equal traffic split
            traffic_split = {f"{provider.value}-{region.value}": 1.0/len(regions) 
                           for provider, region in regions}
        
        costs = {}
        
        for provider, region in regions:
            key = f"{provider.value}-{region.value}"
            split = traffic_split.get(key, 1.0/len(regions))
            
            # Adjust resources based on traffic split
            compute_vcpus = max(2, int(6 * split))
            gpu_instances = max(1, int(2 * split))
            storage_gb = max(100, int(500 * split))
            network_gb = max(500, int(1000 * split))
            
            cost = self.calculate_infrastructure_cost(
                provider=provider,
                region=region,
                compute_vcpus=compute_vcpus,
                gpu_instances=gpu_instances,
                storage_gb=storage_gb,
                network_gb_per_month=network_gb
            )
            
            costs[key] = cost
        
        return costs

class BusinessModelCalculator:
    """Calculate revenue projections and business metrics"""
    
    # Pricing tiers
    PRICING_TIERS = {
        'free': {'price': 0, 'requests': 50},
        'starter': {'price': 10, 'requests': 500},
        'professional': {'price': 50, 'requests': 2500},
        'enterprise': {'price': 200, 'requests': 10000},
        'custom': {'price': 1000, 'requests': 999999}  # Average custom price
    }
    
    # Conversion rates (industry averages)
    CONVERSION_RATES = {
        'free_to_starter': 0.05,    # 5% of free users upgrade to starter
        'starter_to_professional': 0.20,  # 20% of starter users upgrade
        'professional_to_enterprise': 0.15,  # 15% upgrade to enterprise
        'churn_rate_monthly': 0.05   # 5% monthly churn
    }
    
    def __init__(self):
        pass
    
    def project_user_growth(
        self,
        initial_users: int = 100,
        growth_rate_monthly: float = 0.25,  # 25% monthly growth
        months: int = 24
    ) -> List[Dict[str, int]]:
        """Project user growth over time"""
        
        projections = []
        
        # Starting values
        free_users = initial_users
        starter_users = 0
        professional_users = 0
        enterprise_users = 0
        custom_users = 0
        
        for month in range(1, months + 1):
            # New user acquisition (mostly free)
            new_free_users = int(free_users * growth_rate_monthly)
            free_users += new_free_users
            
            # Conversions
            free_to_starter = int(free_users * self.CONVERSION_RATES['free_to_starter'] / 12)  # Monthly conversion
            starter_to_pro = int(starter_users * self.CONVERSION_RATES['starter_to_professional'] / 12)
            pro_to_enterprise = int(professional_users * self.CONVERSION_RATES['professional_to_enterprise'] / 12)
            
            # Apply conversions
            free_users -= free_to_starter
            starter_users += free_to_starter - starter_to_pro
            professional_users += starter_to_pro - pro_to_enterprise
            enterprise_users += pro_to_enterprise
            
            # Custom users (enterprise sales)
            if month > 6:  # Custom sales start after 6 months
                custom_users += max(1, int(enterprise_users * 0.05))  # 5% of enterprise become custom
            
            # Apply churn (except for custom users who have contracts)
            churn_rate = self.CONVERSION_RATES['churn_rate_monthly']
            free_users = int(free_users * (1 - churn_rate))
            starter_users = int(starter_users * (1 - churn_rate))
            professional_users = int(professional_users * (1 - churn_rate))
            enterprise_users = int(enterprise_users * (1 - churn_rate * 0.5))  # Lower churn for enterprise
            
            projections.append({
                'month': month,
                'free_users': free_users,
                'starter_users': starter_users,
                'professional_users': professional_users,
                'enterprise_users': enterprise_users,
                'custom_users': custom_users,
                'total_users': free_users + starter_users + professional_users + enterprise_users + custom_users
            })
        
        return projections
    
    def calculate_revenue_projection(self, user_projection: Dict[str, int]) -> RevenueProjection:
        """Calculate revenue from user numbers"""
        
        monthly_revenue = (
            user_projection['starter_users'] * self.PRICING_TIERS['starter']['price'] +
            user_projection['professional_users'] * self.PRICING_TIERS['professional']['price'] +
            user_projection['enterprise_users'] * self.PRICING_TIERS['enterprise']['price'] +
            user_projection['custom_users'] * self.PRICING_TIERS['custom']['price']
        )
        
        annual_revenue = monthly_revenue * 12
        
        return RevenueProjection(
            free_users=user_projection['free_users'],
            starter_users=user_projection['starter_users'],
            professional_users=user_projection['professional_users'],
            enterprise_users=user_projection['enterprise_users'],
            custom_users=user_projection['custom_users'],
            monthly_revenue=monthly_revenue,
            annual_revenue=annual_revenue
        )
    
    def calculate_break_even_analysis(
        self,
        fixed_costs_monthly: float,
        variable_cost_per_user: float = 2.0,
        target_margin: float = 0.70  # 70% profit margin
    ) -> Dict[str, float]:
        """Calculate break-even points and targets"""
        
        # Average revenue per user (ARPU) across all paid tiers
        total_paid_revenue = (
            self.PRICING_TIERS['starter']['price'] +
            self.PRICING_TIERS['professional']['price'] +
            self.PRICING_TIERS['enterprise']['price']
        )
        # Weighted average (assuming 60% starter, 30% pro, 10% enterprise)
        arpu = (0.6 * self.PRICING_TIERS['starter']['price'] +
                0.3 * self.PRICING_TIERS['professional']['price'] +
                0.1 * self.PRICING_TIERS['enterprise']['price'])
        
        # Break-even calculation
        contribution_margin = arpu - variable_cost_per_user
        break_even_users = math.ceil(fixed_costs_monthly / contribution_margin)
        
        # Target for desired margin
        target_contribution = fixed_costs_monthly / (1 - target_margin)
        target_users = math.ceil(target_contribution / contribution_margin)
        
        return {
            'arpu': arpu,
            'contribution_margin': contribution_margin,
            'break_even_users': break_even_users,
            'target_users_70_margin': target_users,
            'break_even_revenue': break_even_users * arpu,
            'target_revenue_70_margin': target_users * arpu
        }

class CostOptimizer:
    """Optimize costs and suggest improvements"""
    
    def __init__(self, cost_calculator: CostCalculator):
        self.cost_calculator = cost_calculator
    
    def suggest_cost_optimizations(
        self,
        current_cost: InfrastructureCost,
        usage_metrics: Dict[str, float]
    ) -> List[Dict[str, str]]:
        """Suggest cost optimization strategies"""
        
        suggestions = []
        
        # GPU utilization optimization
        if usage_metrics.get('gpu_utilization', 0) < 0.5:
            suggestions.append({
                'category': 'GPU',
                'suggestion': 'Consider using smaller GPU instances or implementing auto-scaling',
                'potential_saving': f'${current_cost.gpu * 0.3:.0f}/month',
                'priority': 'high'
            })
        
        # Compute optimization
        if usage_metrics.get('cpu_utilization', 0) < 0.4:
            suggestions.append({
                'category': 'Compute',
                'suggestion': 'Right-size compute instances based on actual usage',
                'potential_saving': f'${current_cost.compute * 0.25:.0f}/month',
                'priority': 'medium'
            })
        
        # Storage optimization
        if usage_metrics.get('storage_utilization', 0) < 0.6:
            suggestions.append({
                'category': 'Storage',
                'suggestion': 'Implement data lifecycle policies and compression',
                'potential_saving': f'${current_cost.storage * 0.4:.0f}/month',
                'priority': 'low'
            })
        
        # Network optimization
        if current_cost.network > 100:
            suggestions.append({
                'category': 'Network',
                'suggestion': 'Implement CDN and optimize data transfer patterns',
                'potential_saving': f'${current_cost.network * 0.3:.0f}/month',
                'priority': 'medium'
            })
        
        return suggestions
    
    def compare_cloud_providers(
        self,
        region: Region = Region.US_EAST_1
    ) -> Dict[str, Dict[str, float]]:
        """Compare costs across cloud providers"""
        
        comparison = {}
        
        for provider in CloudProvider:
            cost = self.cost_calculator.calculate_infrastructure_cost(
                provider=provider,
                region=region
            )
            
            comparison[provider.value] = {
                'total_cost': cost.total,
                'compute_cost': cost.compute,
                'gpu_cost': cost.gpu,
                'storage_cost': cost.storage,
                'network_cost': cost.network
            }
        
        return comparison

def generate_comprehensive_report():
    """Generate a comprehensive cost and business model report"""
    
    print("💰 DevOps/SRE MCP Server - Cost Analysis & Business Model")
    print("=" * 70)
    
    cost_calc = CostCalculator()
    business_calc = BusinessModelCalculator()
    optimizer = CostOptimizer(cost_calc)
    
    # Calculate infrastructure costs for different scenarios
    print("\n🏗️  INFRASTRUCTURE COSTS")
    print("-" * 30)
    
    scenarios = [
        ("AWS Production", CloudProvider.AWS, Region.US_EAST_1, True),
        ("GCP Production", CloudProvider.GCP, Region.US_EAST_1, True),
        ("Azure Production", CloudProvider.AZURE, Region.US_EAST_1, True),
        ("AWS Development", CloudProvider.AWS, Region.US_EAST_1, False)
    ]
    
    for name, provider, region, is_prod in scenarios:
        env = "production" if is_prod else "development"
        cost = cost_calc.calculate_infrastructure_cost(
            provider=provider,
            region=region,
            enable_ha=is_prod,
            environment=env
        )
        
        print(f"\n{name}:")
        print(f"  Total: ${cost.total:,.2f}/month")
        print(f"  Compute: ${cost.compute:,.2f} | GPU: ${cost.gpu:,.2f}")
        print(f"  Storage: ${cost.storage:,.2f} | Network: ${cost.network:,.2f}")
        print(f"  Database: ${cost.database:,.2f} | Cache: ${cost.cache:,.2f}")
    
    # Multi-cloud scenario
    print(f"\n🌐 Multi-Cloud Deployment:")
    multi_cloud_regions = [
        (CloudProvider.AWS, Region.US_EAST_1),
        (CloudProvider.GCP, Region.EU_WEST_1),
        (CloudProvider.AZURE, Region.AP_SOUTHEAST_1)
    ]
    
    multi_costs = cost_calc.calculate_multi_cloud_cost(multi_cloud_regions)
    total_multi_cost = sum(cost.total for cost in multi_costs.values())
    print(f"  Total Multi-Cloud Cost: ${total_multi_cost:,.2f}/month")
    
    # Operational costs
    print(f"\n👥 OPERATIONAL COSTS")
    print("-" * 20)
    
    op_cost = cost_calc.calculate_operational_cost(
        team_size=3,
        support_tier="premium",
        marketing_budget=8000
    )
    
    print(f"  Staff: ${op_cost.staff:,.2f}/month")
    print(f"  Support: ${op_cost.support:,.2f}/month")
    print(f"  Marketing: ${op_cost.marketing:,.2f}/month")
    print(f"  Total Operational: ${op_cost.total:,.2f}/month")
    
    # Total costs
    aws_infra_cost = cost_calc.calculate_infrastructure_cost(CloudProvider.AWS, Region.US_EAST_1)
    total_monthly_cost = aws_infra_cost.total + op_cost.total
    
    print(f"\n💸 TOTAL COSTS")
    print("-" * 15)
    print(f"  Infrastructure: ${aws_infra_cost.total:,.2f}/month")
    print(f"  Operational: ${op_cost.total:,.2f}/month")
    print(f"  TOTAL: ${total_monthly_cost:,.2f}/month")
    print(f"  Annual: ${total_monthly_cost * 12:,.2f}/year")
    
    # Revenue projections
    print(f"\n📈 REVENUE PROJECTIONS")
    print("-" * 25)
    
    user_growth = business_calc.project_user_growth(initial_users=200, months=24)
    
    key_months = [1, 6, 12, 18, 24]
    for month in key_months:
        projection = user_growth[month - 1]
        revenue = business_calc.calculate_revenue_projection(projection)
        
        print(f"\nMonth {month}:")
        print(f"  Users: {projection['total_users']:,} total "
              f"({projection['starter_users']} starter, "
              f"{projection['professional_users']} pro, "
              f"{projection['enterprise_users']} enterprise)")
        print(f"  Revenue: ${revenue.monthly_revenue:,.0f}/month "
              f"(${revenue.annual_revenue:,.0f}/year)")
        
        # Profit calculation
        profit = revenue.monthly_revenue - total_monthly_cost
        margin = (profit / revenue.monthly_revenue * 100) if revenue.monthly_revenue > 0 else 0
        print(f"  Profit: ${profit:,.0f}/month ({margin:.1f}% margin)")
    
    # Break-even analysis
    print(f"\n⚖️  BREAK-EVEN ANALYSIS")
    print("-" * 25)
    
    break_even = business_calc.calculate_break_even_analysis(
        fixed_costs_monthly=total_monthly_cost,
        variable_cost_per_user=3.0
    )
    
    print(f"  ARPU: ${break_even['arpu']:.2f}")
    print(f"  Break-even users: {break_even['break_even_users']:,}")
    print(f"  Break-even revenue: ${break_even['break_even_revenue']:,.0f}/month")
    print(f"  Target users (70% margin): {break_even['target_users_70_margin']:,}")
    print(f"  Target revenue (70% margin): ${break_even['target_revenue_70_margin']:,.0f}/month")
    
    # Find break-even month
    break_even_month = None
    for i, projection in enumerate(user_growth):
        revenue = business_calc.calculate_revenue_projection(projection)
        if revenue.monthly_revenue >= break_even['break_even_revenue']:
            break_even_month = i + 1
            break
    
    if break_even_month:
        print(f"  Projected break-even: Month {break_even_month}")
    
    # Cost optimization suggestions
    print(f"\n🔧 COST OPTIMIZATION")
    print("-" * 22)
    
    usage_metrics = {
        'gpu_utilization': 0.6,
        'cpu_utilization': 0.45,
        'storage_utilization': 0.7
    }
    
    suggestions = optimizer.suggest_cost_optimizations(aws_infra_cost, usage_metrics)
    
    for suggestion in suggestions:
        print(f"  {suggestion['category']}: {suggestion['suggestion']}")
        print(f"    Potential saving: {suggestion['potential_saving']} ({suggestion['priority']} priority)")
    
    # Summary and recommendations
    print(f"\n🎯 SUMMARY & RECOMMENDATIONS")
    print("-" * 35)
    
    print(f"✅ Phase 1 (Months 1-6): Start with single cloud (AWS)")
    print(f"   - Cost: ${aws_infra_cost.total:,.0f}/month infrastructure")
    print(f"   - Target: {break_even['break_even_users']:,} paid users to break even")
    
    print(f"\n✅ Phase 2 (Months 7-12): Expand to multi-cloud")
    print(f"   - Cost: ${total_multi_cost:,.0f}/month infrastructure")
    print(f"   - Target: 70% profit margin at {break_even['target_users_70_margin']:,} users")
    
    print(f"\n✅ Phase 3 (Months 13+): Scale and optimize")
    print(f"   - Implement cost optimizations")
    print(f"   - Focus on enterprise and custom tiers")
    print(f"   - Target: $500K+ ARR by month 24")
    
    print(f"\n💡 Key Success Factors:")
    print(f"   - Achieve 25% monthly user growth")
    print(f"   - Maintain 5% conversion rate from free to paid")
    print(f"   - Keep churn below 5% monthly")
    print(f"   - Focus on high-value enterprise customers")
    
    return {
        'infrastructure_cost': aws_infra_cost,
        'operational_cost': op_cost,
        'total_monthly_cost': total_monthly_cost,
        'break_even_analysis': break_even,
        'user_projections': user_growth,
        'optimization_suggestions': suggestions
    }

if __name__ == "__main__":
    results = generate_comprehensive_report()
