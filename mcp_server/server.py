#!/usr/bin/env python3
"""
Advanced MCP Server for DevOps, Cloud, SRE, and Platform Engineering
Optimized for gpt-oss:latest model with industry-level expertise
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel,
    )
except ImportError:
    print("MCP library not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"], check=True)
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel,
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("devops-mcp-server")

@dataclass
class DevOpsContext:
    """Context for DevOps operations"""
    environment: str = "production"
    region: str = "us-west-2"
    cluster: str = "main"
    namespace: str = "default"
    service: str = ""
    version: str = ""
    
@dataclass
class AnalysisResult:
    """Structured analysis result"""
    analysis_id: str
    timestamp: str
    category: str
    severity: str
    confidence: float
    findings: List[str]
    recommendations: List[str]
    metrics: Dict[str, Any]

class DevOpsMCPServer:
    """Advanced MCP Server for DevOps, SRE, Cloud, and Platform Engineering"""
    
    def __init__(self):
        self.server = Server("devops-sre-platform-server")
        self.model = "gpt-oss:latest"
        self.context = DevOpsContext()
        self.analysis_history = []
        
        # Industry-specific prompts and configurations
        self.load_industry_prompts()
        
        # Register tools and resources
        self.register_tools()
        self.register_resources()
    
    def load_industry_prompts(self):
        """Load industry-level prompts for different domains"""
        self.prompts = {
            "devops": {
                "system_prompt": """You are a Senior DevOps Engineer with 15+ years of experience in enterprise environments. You specialize in:
- CI/CD pipeline optimization and troubleshooting
- Infrastructure as Code (Terraform, CloudFormation, Ansible)
- Container orchestration (Kubernetes, Docker Swarm)
- Cloud platforms (AWS, Azure, GCP, multi-cloud strategies)
- Monitoring and observability (Prometheus, Grafana, ELK stack)
- Security best practices and compliance (SOC2, PCI-DSS, HIPAA)
- Performance optimization and cost management
- Incident response and post-mortem analysis
- GitOps workflows and automation

You provide actionable, production-ready solutions with security and scalability in mind. Always include cost implications and performance impact in your recommendations.""",
                
                "analysis_template": """Analyze the following DevOps scenario and provide comprehensive recommendations:

**Context**: {context}
**Issue/Request**: {input}

Provide analysis in the following areas:
1. **Root Cause Analysis**: Identify underlying issues
2. **Impact Assessment**: Business and technical impact
3. **Solution Architecture**: Detailed technical solution
4. **Implementation Plan**: Step-by-step execution
5. **Risk Mitigation**: Potential risks and mitigation strategies
6. **Cost Analysis**: Resource and operational costs
7. **Performance Impact**: Expected performance improvements
8. **Security Considerations**: Security implications and requirements
9. **Monitoring & Alerting**: Observability recommendations
10. **Rollback Strategy**: Contingency planning

Format response as structured JSON with confidence scores."""
            },
            
            "sre": {
                "system_prompt": """You are a Principal Site Reliability Engineer with expertise in large-scale distributed systems. You excel at:
- Service Level Objectives (SLOs) and Error Budgets
- Incident management and post-mortem culture
- Reliability engineering and chaos engineering
- Performance optimization and capacity planning
- Observability and monitoring strategy
- On-call procedures and escalation policies
- Disaster recovery and business continuity
- Automation and toil reduction
- Service mesh and microservices architecture
- Database reliability and data consistency

You focus on measurable reliability improvements and data-driven decisions. Always quantify reliability metrics and provide SLO recommendations.""",
                
                "analysis_template": """Perform SRE analysis for the following scenario:

**Service Context**: {context}
**Reliability Issue**: {input}

Provide comprehensive SRE analysis:
1. **Service Level Analysis**: Current SLIs, SLOs, and error budget status
2. **Reliability Assessment**: System reliability evaluation
3. **Failure Mode Analysis**: Potential failure modes and impact
4. **Observability Gaps**: Missing monitoring and alerting
5. **Capacity Planning**: Resource requirements and scaling needs
6. **Incident Response**: Runbook and escalation procedures
7. **Chaos Engineering**: Resilience testing recommendations
8. **Toil Reduction**: Automation opportunities
9. **Performance Optimization**: Latency and throughput improvements
10. **Recovery Procedures**: Disaster recovery and backup strategies

Include quantitative metrics and reliability targets."""
            },
            
            "cloud": {
                "system_prompt": """You are a Senior Cloud Architect with deep expertise across AWS, Azure, and GCP. You specialize in:
- Cloud-native architecture design and migration strategies
- Multi-cloud and hybrid cloud solutions
- Serverless computing and event-driven architectures
- Cloud security and compliance frameworks
- Cost optimization and FinOps practices
- Auto-scaling and resource management
- Data lakes, warehouses, and analytics platforms
- Network architecture and connectivity solutions
- Identity and access management (IAM)
- Cloud governance and policy management

You design scalable, secure, and cost-effective cloud solutions following well-architected frameworks.""",
                
                "analysis_template": """Analyze the cloud architecture scenario:

**Cloud Environment**: {context}
**Architecture Challenge**: {input}

Provide cloud architecture analysis:
1. **Architecture Assessment**: Current state evaluation
2. **Well-Architected Review**: Pillars assessment (Security, Reliability, Performance, Cost, Operational Excellence)
3. **Migration Strategy**: Cloud adoption and migration path
4. **Security Architecture**: Identity, network, and data security
5. **Cost Optimization**: Resource optimization and cost management
6. **Scalability Design**: Auto-scaling and elasticity patterns
7. **Disaster Recovery**: Multi-region and backup strategies
8. **Compliance Requirements**: Regulatory and governance needs
9. **Integration Patterns**: API and service integration
10. **Monitoring Strategy**: Cloud-native observability

Include cost estimates and performance benchmarks."""
            },
            
            "platform": {
                "system_prompt": """You are a Staff Platform Engineer building developer platforms and internal tools. You excel at:
- Developer experience and productivity optimization
- Platform engineering and internal developer platforms
- API design and microservices architecture
- Service mesh and traffic management
- Developer tooling and CI/CD platforms
- Infrastructure abstraction and self-service
- Golden paths and paved roads for developers
- Platform reliability and service level agreements
- Resource management and multi-tenancy
- Documentation and onboarding automation

You focus on enabling developer velocity while maintaining operational excellence.""",
                
                "analysis_template": """Analyze the platform engineering scenario:

**Platform Context**: {context}
**Platform Challenge**: {input}

Provide platform engineering analysis:
1. **Developer Experience**: Current pain points and opportunities
2. **Platform Architecture**: Internal platform design and components
3. **Self-Service Capabilities**: Developer self-service features
4. **API Strategy**: Platform API design and governance
5. **Tooling Integration**: CI/CD and developer tool integration
6. **Resource Abstraction**: Infrastructure and service abstraction
7. **Multi-tenancy**: Tenant isolation and resource sharing
8. **Platform Reliability**: SLAs and platform stability
9. **Onboarding Experience**: Developer onboarding and documentation
10. **Metrics & Analytics**: Platform usage and productivity metrics

Focus on developer productivity and platform adoption."""
            }
        }
    
    def register_tools(self):
        """Register MCP tools for DevOps operations"""
        
        @self.server.call_tool()
        async def analyze_logs(
            logs: str,
            analysis_type: str = "devops",
            context: Optional[str] = None
        ) -> List[TextContent]:
            """Analyze logs using domain-specific expertise"""
            return await self.analyze_with_ollama(logs, analysis_type, context)
        
        @self.server.call_tool()
        async def infrastructure_audit(
            infrastructure_config: str,
            cloud_provider: str = "aws",
            compliance_framework: str = "soc2"
        ) -> List[TextContent]:
            """Perform infrastructure security and compliance audit"""
            return await self.audit_infrastructure(infrastructure_config, cloud_provider, compliance_framework)
        
        @self.server.call_tool()
        async def incident_analysis(
            incident_data: str,
            severity: str = "high",
            service_context: Optional[str] = None
        ) -> List[TextContent]:
            """Analyze incidents and provide post-mortem insights"""
            return await self.analyze_incident(incident_data, severity, service_context)
        
        @self.server.call_tool()
        async def performance_analysis(
            metrics_data: str,
            analysis_period: str = "24h",
            service_name: Optional[str] = None
        ) -> List[TextContent]:
            """Analyze performance metrics and provide optimization recommendations"""
            return await self.analyze_performance(metrics_data, analysis_period, service_name)
        
        @self.server.call_tool()
        async def capacity_planning(
            usage_data: str,
            growth_projection: str = "20%",
            time_horizon: str = "6months"
        ) -> List[TextContent]:
            """Perform capacity planning analysis"""
            return await self.plan_capacity(usage_data, growth_projection, time_horizon)
        
        @self.server.call_tool()
        async def security_assessment(
            security_logs: str,
            threat_model: str = "owasp",
            environment: str = "production"
        ) -> List[TextContent]:
            """Perform security assessment and threat analysis"""
            return await self.assess_security(security_logs, threat_model, environment)
        
        @self.server.call_tool()
        async def cost_optimization(
            cost_data: str,
            optimization_target: str = "30%",
            cloud_provider: str = "aws"
        ) -> List[TextContent]:
            """Analyze costs and provide optimization recommendations"""
            return await self.optimize_costs(cost_data, optimization_target, cloud_provider)
        
        @self.server.call_tool()
        async def disaster_recovery_plan(
            system_architecture: str,
            rto_requirement: str = "4h",
            rpo_requirement: str = "1h"
        ) -> List[TextContent]:
            """Generate disaster recovery and business continuity plan"""
            return await self.plan_disaster_recovery(system_architecture, rto_requirement, rpo_requirement)
    
    def register_resources(self):
        """Register MCP resources for DevOps knowledge base"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available DevOps resources and knowledge base"""
            return [
                Resource(
                    uri="devops://best-practices/ci-cd",
                    name="CI/CD Best Practices",
                    description="Industry best practices for CI/CD pipelines",
                    mimeType="text/markdown"
                ),
                Resource(
                    uri="devops://templates/kubernetes",
                    name="Kubernetes Templates",
                    description="Production-ready Kubernetes manifests and Helm charts",
                    mimeType="application/yaml"
                ),
                Resource(
                    uri="devops://runbooks/incident-response",
                    name="Incident Response Runbooks",
                    description="Standardized incident response procedures",
                    mimeType="text/markdown"
                ),
                Resource(
                    uri="devops://monitoring/slo-templates",
                    name="SLO Templates",
                    description="Service Level Objective templates and examples",
                    mimeType="application/json"
                ),
                Resource(
                    uri="devops://security/compliance-checklists",
                    name="Compliance Checklists",
                    description="Security and compliance validation checklists",
                    mimeType="text/markdown"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read DevOps resource content"""
            return await self.get_resource_content(uri)
    
    async def analyze_with_ollama(self, logs: str, analysis_type: str, context: Optional[str] = None) -> List[TextContent]:
        """Analyze logs using Ollama with domain-specific prompts"""
        try:
            # Get appropriate prompt for analysis type
            prompt_config = self.prompts.get(analysis_type, self.prompts["devops"])
            
            # Prepare context
            analysis_context = context or f"Environment: {self.context.environment}, Service: {self.context.service}"
            
            # Build full prompt
            system_prompt = prompt_config["system_prompt"]
            user_prompt = prompt_config["analysis_template"].format(
                context=analysis_context,
                input=logs
            )
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Run analysis with Ollama
            result = await self.run_ollama_analysis(full_prompt, temperature=0.1)
            
            # Parse and structure result
            analysis_result = self.parse_analysis_result(result, analysis_type)
            
            # Store in history
            self.analysis_history.append(analysis_result)
            
            return [TextContent(
                type="text",
                text=json.dumps(asdict(analysis_result), indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return [TextContent(
                type="text",
                text=f"Analysis failed: {str(e)}"
            )]
    
    async def run_ollama_analysis(self, prompt: str, temperature: float = 0.1) -> str:
        """Run analysis using Ollama with performance optimizations"""
        try:
            # Create temporary file for the prompt (better for large prompts)
            temp_file = f"/tmp/devops_mcp_prompt_{uuid.uuid4()}.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Optimize Ollama parameters for performance
            cmd = [
                "ollama", "run", self.model,
                "--temperature", str(temperature),
                "--top-p", "0.9",
                "--top-k", "40",
                "--repeat-penalty", "1.1",
                "--num-ctx", "32768",  # Larger context for complex analysis
                "--num-predict", "4096"  # Allow longer responses
            ]
            
            # Run with optimized settings
            with open(temp_file, 'r', encoding='utf-8') as f:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=f,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            # Clean up temp file
            os.remove(temp_file)
            
            if process.returncode == 0:
                return stdout.decode('utf-8').strip()
            else:
                raise Exception(f"Ollama error: {stderr.decode('utf-8')}")
                
        except asyncio.TimeoutError:
            raise Exception("Analysis timed out after 5 minutes")
        except Exception as e:
            raise Exception(f"Ollama execution failed: {str(e)}")
    
    def parse_analysis_result(self, result: str, analysis_type: str) -> AnalysisResult:
        """Parse and structure analysis result"""
        try:
            # Try to parse as JSON first
            if result.strip().startswith('{'):
                parsed = json.loads(result)
                return AnalysisResult(
                    analysis_id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    category=analysis_type,
                    severity=parsed.get('severity', 'medium'),
                    confidence=parsed.get('confidence', 0.8),
                    findings=parsed.get('findings', []),
                    recommendations=parsed.get('recommendations', []),
                    metrics=parsed.get('metrics', {})
                )
            else:
                # Parse structured text response
                return self.parse_text_result(result, analysis_type)
                
        except json.JSONDecodeError:
            # Fallback to text parsing
            return self.parse_text_result(result, analysis_type)
    
    def parse_text_result(self, result: str, analysis_type: str) -> AnalysisResult:
        """Parse text-based analysis result"""
        lines = result.split('\n')
        findings = []
        recommendations = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'finding' in line.lower() or 'issue' in line.lower():
                current_section = 'findings'
            elif 'recommend' in line.lower() or 'solution' in line.lower():
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('*') or line.startswith('•'):
                if current_section == 'findings':
                    findings.append(line[1:].strip())
                elif current_section == 'recommendations':
                    recommendations.append(line[1:].strip())
        
        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            category=analysis_type,
            severity='medium',
            confidence=0.8,
            findings=findings or [result[:200] + "..."],
            recommendations=recommendations or ["See detailed analysis above"],
            metrics={'response_length': len(result)}
        )
    
    async def audit_infrastructure(self, config: str, provider: str, framework: str) -> List[TextContent]:
        """Perform infrastructure audit"""
        audit_prompt = f"""
        As a cloud security expert, audit the following infrastructure configuration:
        
        Provider: {provider}
        Compliance Framework: {framework}
        Configuration: {config}
        
        Provide a comprehensive security and compliance audit including:
        1. Security vulnerabilities and misconfigurations
        2. Compliance violations and gaps
        3. Best practice recommendations
        4. Risk assessment and prioritization
        5. Remediation steps with implementation details
        """
        
        result = await self.run_ollama_analysis(audit_prompt)
        return [TextContent(type="text", text=result)]
    
    async def analyze_incident(self, incident_data: str, severity: str, context: Optional[str]) -> List[TextContent]:
        """Analyze incident for post-mortem"""
        incident_prompt = f"""
        As an SRE expert, analyze this incident for post-mortem:
        
        Severity: {severity}
        Context: {context or 'Not provided'}
        Incident Data: {incident_data}
        
        Provide comprehensive incident analysis:
        1. Timeline reconstruction and root cause analysis
        2. Impact assessment (users, revenue, SLA impact)
        3. Contributing factors and failure modes
        4. Detection and response timeline analysis
        5. Action items and preventive measures
        6. Process improvements and lessons learned
        7. Monitoring and alerting recommendations
        """
        
        result = await self.run_ollama_analysis(incident_prompt)
        return [TextContent(type="text", text=result)]
    
    async def analyze_performance(self, metrics: str, period: str, service: Optional[str]) -> List[TextContent]:
        """Analyze performance metrics"""
        performance_prompt = f"""
        As a performance engineering expert, analyze these metrics:
        
        Time Period: {period}
        Service: {service or 'Not specified'}
        Metrics Data: {metrics}
        
        Provide performance analysis:
        1. Performance trend analysis and bottleneck identification
        2. Resource utilization and capacity assessment
        3. Latency analysis and optimization opportunities
        4. Throughput analysis and scaling recommendations
        5. Error rate analysis and reliability impact
        6. Cost-performance optimization suggestions
        7. Monitoring and alerting thresholds
        """
        
        result = await self.run_ollama_analysis(performance_prompt)
        return [TextContent(type="text", text=result)]
    
    async def plan_capacity(self, usage_data: str, growth: str, horizon: str) -> List[TextContent]:
        """Perform capacity planning"""
        capacity_prompt = f"""
        As a capacity planning expert, analyze current usage and plan for growth:
        
        Current Usage: {usage_data}
        Growth Projection: {growth}
        Planning Horizon: {horizon}
        
        Provide capacity planning analysis:
        1. Current utilization analysis and trends
        2. Growth projection modeling and scenarios
        3. Resource requirements and scaling timeline
        4. Cost projections and budget planning
        5. Risk assessment and contingency planning
        6. Technology alternatives and trade-offs
        7. Implementation roadmap and milestones
        """
        
        result = await self.run_ollama_analysis(capacity_prompt)
        return [TextContent(type="text", text=result)]
    
    async def assess_security(self, logs: str, threat_model: str, environment: str) -> List[TextContent]:
        """Perform security assessment"""
        security_prompt = f"""
        As a cybersecurity expert, analyze these security logs:
        
        Environment: {environment}
        Threat Model: {threat_model}
        Security Logs: {logs}
        
        Provide comprehensive security assessment:
        1. Threat detection and attack pattern analysis
        2. Vulnerability assessment and risk scoring
        3. Compliance status and regulatory requirements
        4. Incident response recommendations
        5. Security control effectiveness evaluation
        6. Threat hunting and proactive measures
        7. Security architecture improvements
        """
        
        result = await self.run_ollama_analysis(security_prompt)
        return [TextContent(type="text", text=result)]
    
    async def optimize_costs(self, cost_data: str, target: str, provider: str) -> List[TextContent]:
        """Analyze and optimize costs"""
        cost_prompt = f"""
        As a FinOps expert, analyze costs and provide optimization recommendations:
        
        Cloud Provider: {provider}
        Optimization Target: {target}
        Cost Data: {cost_data}
        
        Provide cost optimization analysis:
        1. Cost breakdown and trend analysis
        2. Resource utilization and waste identification
        3. Right-sizing recommendations and savings potential
        4. Reserved instance and savings plan opportunities
        5. Architecture optimization for cost efficiency
        6. Governance and policy recommendations
        7. Implementation roadmap and ROI projections
        """
        
        result = await self.run_ollama_analysis(cost_prompt)
        return [TextContent(type="text", text=result)]
    
    async def plan_disaster_recovery(self, architecture: str, rto: str, rpo: str) -> List[TextContent]:
        """Generate disaster recovery plan"""
        dr_prompt = f"""
        As a business continuity expert, create a disaster recovery plan:
        
        System Architecture: {architecture}
        Recovery Time Objective (RTO): {rto}
        Recovery Point Objective (RPO): {rpo}
        
        Provide comprehensive DR plan:
        1. Risk assessment and failure scenarios
        2. Recovery strategy and architecture design
        3. Backup and replication strategies
        4. Recovery procedures and runbooks
        5. Testing and validation protocols
        6. Communication and escalation plans
        7. Cost analysis and optimization
        """
        
        result = await self.run_ollama_analysis(dr_prompt)
        return [TextContent(type="text", text=result)]
    
    async def get_resource_content(self, uri: str) -> str:
        """Get content for DevOps resources"""
        resource_map = {
            "devops://best-practices/ci-cd": self.get_cicd_best_practices(),
            "devops://templates/kubernetes": self.get_kubernetes_templates(),
            "devops://runbooks/incident-response": self.get_incident_runbooks(),
            "devops://monitoring/slo-templates": self.get_slo_templates(),
            "devops://security/compliance-checklists": self.get_compliance_checklists()
        }
        
        return resource_map.get(uri, "Resource not found")
    
    def get_cicd_best_practices(self) -> str:
        """Return CI/CD best practices"""
        return """
# CI/CD Best Practices

## Pipeline Design
- Use declarative pipelines (Jenkinsfile, GitHub Actions YAML)
- Implement pipeline as code with version control
- Use parallel execution for independent tasks
- Implement proper error handling and notifications

## Security
- Scan for vulnerabilities in dependencies
- Use secure secret management (HashiCorp Vault, AWS Secrets Manager)
- Implement least privilege access principles
- Sign and verify artifacts

## Testing Strategy
- Unit tests with >80% coverage
- Integration tests for API contracts
- End-to-end tests for critical user journeys
- Performance tests for baseline validation

## Deployment Patterns
- Blue-green deployments for zero downtime
- Canary releases for gradual rollouts
- Feature flags for safe feature delivery
- Automated rollback on failure detection

## Monitoring and Observability
- Implement deployment metrics and alerts
- Track DORA metrics (deployment frequency, lead time, MTTR, change failure rate)
- Use distributed tracing for complex systems
- Monitor business metrics alongside technical metrics
        """
    
    def get_kubernetes_templates(self) -> str:
        """Return Kubernetes templates"""
        return """
# Production-Ready Kubernetes Templates

## Deployment Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  labels:
    app: myapp
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: v1.0.0
    spec:
      containers:
      - name: app
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Service Template
```yaml
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
```

## HPA Template
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```
        """
    
    def get_incident_runbooks(self) -> str:
        """Return incident response runbooks"""
        return """
# Incident Response Runbooks

## Severity Classification
- **P0 (Critical)**: Complete service outage, data loss, security breach
- **P1 (High)**: Major feature unavailable, significant performance degradation
- **P2 (Medium)**: Minor feature issues, limited user impact
- **P3 (Low)**: Cosmetic issues, no user impact

## Response Procedures

### P0/P1 Incident Response
1. **Detection** (0-5 minutes)
   - Alert received via monitoring system
   - On-call engineer acknowledges within 5 minutes
   - Initial triage and severity assessment

2. **Response** (5-15 minutes)
   - Create incident channel (#incident-YYYY-MM-DD-NNNN)
   - Page incident commander for P0 incidents
   - Engage subject matter experts
   - Begin investigation and mitigation

3. **Communication** (15-30 minutes)
   - Update status page with initial communication
   - Notify stakeholders via predetermined channels
   - Provide regular updates every 30 minutes

4. **Resolution** (Ongoing)
   - Implement temporary workaround if possible
   - Develop and deploy permanent fix
   - Verify resolution and monitor for regression
   - Update status page with resolution

5. **Post-Mortem** (24-48 hours)
   - Conduct blameless post-mortem
   - Document timeline and root cause
   - Identify action items and owners
   - Update runbooks and monitoring

## Communication Templates
- **Initial Alert**: "We are investigating reports of [issue]. Updates to follow."
- **Update**: "We have identified the cause as [root cause] and are implementing a fix."
- **Resolution**: "The issue has been resolved. All systems are operating normally."
        """
    
    def get_slo_templates(self) -> str:
        """Return SLO templates"""
        return """
{
  "service_level_objectives": {
    "web_service": {
      "availability": {
        "sli": "ratio of successful HTTP requests",
        "slo": "99.9% over 30 days",
        "error_budget": "0.1% (43.2 minutes/month)",
        "measurement": "sum(http_requests_total{code!~\"5..\"})/sum(http_requests_total)"
      },
      "latency": {
        "sli": "95th percentile response time",
        "slo": "< 200ms over 30 days",
        "measurement": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
      }
    },
    "api_service": {
      "availability": {
        "sli": "ratio of successful API calls",
        "slo": "99.95% over 30 days",
        "error_budget": "0.05% (21.6 minutes/month)"
      },
      "throughput": {
        "sli": "requests per second",
        "slo": "> 1000 RPS during peak hours",
        "measurement": "rate(api_requests_total[5m])"
      }
    },
    "data_pipeline": {
      "freshness": {
        "sli": "age of most recent processed record",
        "slo": "< 5 minutes over 30 days",
        "measurement": "time() - pipeline_last_processed_timestamp"
      },
      "completeness": {
        "sli": "ratio of successfully processed records",
        "slo": "99.9% over 30 days",
        "measurement": "pipeline_processed_records/pipeline_input_records"
      }
    }
  },
  "alerting_rules": {
    "slo_burn_rate": {
      "description": "Alert when error budget burn rate is too high",
      "rules": [
        {
          "name": "High burn rate (2h)",
          "condition": "burn_rate > 14.4 for 2m",
          "action": "page immediately"
        },
        {
          "name": "Medium burn rate (6h)",
          "condition": "burn_rate > 6 for 15m",
          "action": "create ticket"
        }
      ]
    }
  }
}
        """
    
    def get_compliance_checklists(self) -> str:
        """Return compliance checklists"""
        return """
# Security and Compliance Checklists

## SOC 2 Type II Compliance

### Access Controls
- [ ] Multi-factor authentication enabled for all users
- [ ] Role-based access control implemented
- [ ] Regular access reviews conducted quarterly
- [ ] Privileged access monitored and logged
- [ ] Automated user provisioning/deprovisioning

### System Operations
- [ ] Change management process documented and followed
- [ ] System monitoring and alerting in place
- [ ] Incident response procedures documented
- [ ] Business continuity plan tested annually
- [ ] Vulnerability management program active

### Data Protection
- [ ] Data encryption at rest and in transit
- [ ] Data classification and handling procedures
- [ ] Backup and recovery procedures tested
- [ ] Data retention policies implemented
- [ ] Secure data disposal procedures

## PCI DSS Compliance

### Network Security
- [ ] Firewall configuration standards maintained
- [ ] Network segmentation implemented
- [ ] Wireless networks secured with WPA2/WPA3
- [ ] Network access controls in place
- [ ] Regular network security testing

### Data Protection
- [ ] Cardholder data encryption
- [ ] Secure key management procedures
- [ ] Data masking in non-production environments
- [ ] Secure data transmission protocols
- [ ] Regular data discovery scans

## GDPR Compliance

### Data Processing
- [ ] Legal basis for processing documented
- [ ] Data processing records maintained
- [ ] Privacy impact assessments conducted
- [ ] Data minimization principles applied
- [ ] Consent management system implemented

### Individual Rights
- [ ] Data subject request procedures
- [ ] Right to be forgotten implementation
- [ ] Data portability capabilities
- [ ] Breach notification procedures (72 hours)
- [ ] Privacy by design implementation
        """

async def main():
    """Main entry point for the MCP server"""
    server_instance = DevOpsMCPServer()
    
    # Initialize server with options
    options = InitializationOptions(
        server_name="DevOps SRE Platform MCP Server",
        server_version="1.0.0",
        capabilities={
            "tools": True,
            "resources": True,
            "logging": True
        }
    )
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())
