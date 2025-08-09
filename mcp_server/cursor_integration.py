#!/usr/bin/env python3
"""
InfraGenius MCP Server for Cursor Integration
Provides specialized DevOps, SRE, Cloud, and Platform Engineering expertise
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        GetPromptRequest,
        GetPromptResult,
        ListPromptsRequest,
        ListPromptsResult,
        ListResourcesRequest,
        ListResourcesResult,
        ListToolsRequest,
        ListToolsResult,
        Prompt,
        PromptArgument,
        PromptMessage,
        Resource,
        TextContent,
        Tool,
    )
except ImportError:
    print("MCP library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        GetPromptRequest,
        GetPromptResult,
        ListPromptsRequest,
        ListPromptsResult,
        ListToolsRequest,
        ListToolsResult,
        Prompt,
        PromptArgument,
        PromptMessage,
        TextContent,
        Tool,
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
server = Server("infragenius")

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:latest")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available InfraGenius tools for Cursor."""
    return ListToolsResult(
        tools=[
            Tool(
                name="analyze_devops_issue",
                description="🔧 Analyze DevOps issues with expert guidance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The DevOps issue or question to analyze"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context (environment, stack, etc.)"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Issue urgency level",
                            "default": "medium"
                        }
                    },
                    "required": ["prompt"]
                }
            ),
            Tool(
                name="analyze_sre_incident",
                description="🚨 SRE incident analysis and response guidance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "incident": {
                            "type": "string",
                            "description": "Description of the incident"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Incident severity level"
                        },
                        "affected_services": {
                            "type": "string",
                            "description": "Services affected by the incident"
                        }
                    },
                    "required": ["incident"]
                }
            ),
            Tool(
                name="review_cloud_architecture",
                description="☁️ Cloud architecture review and optimization",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "architecture": {
                            "type": "string",
                            "description": "Description or diagram of the architecture"
                        },
                        "cloud_provider": {
                            "type": "string",
                            "enum": ["aws", "azure", "gcp", "multi-cloud"],
                            "description": "Primary cloud provider"
                        },
                        "focus_area": {
                            "type": "string",
                            "enum": ["cost", "security", "performance", "scalability", "reliability"],
                            "description": "Primary focus for the review"
                        }
                    },
                    "required": ["architecture"]
                }
            ),
            Tool(
                name="generate_config",
                description="⚙️ Generate configuration files for DevOps tools",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "enum": [
                                "kubernetes", "docker", "terraform", "ansible", 
                                "prometheus", "grafana", "nginx", "apache",
                                "github-actions", "gitlab-ci", "jenkins"
                            ],
                            "description": "Tool to generate configuration for"
                        },
                        "requirements": {
                            "type": "string",
                            "description": "Specific requirements and use case"
                        },
                        "environment": {
                            "type": "string",
                            "enum": ["development", "staging", "production"],
                            "description": "Target environment",
                            "default": "production"
                        }
                    },
                    "required": ["tool", "requirements"]
                }
            ),
            Tool(
                name="explain_logs",
                description="📋 Analyze and explain log files and errors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "logs": {
                            "type": "string",
                            "description": "Log content or error messages to analyze"
                        },
                        "log_type": {
                            "type": "string",
                            "enum": [
                                "application", "system", "kubernetes", "docker", 
                                "nginx", "apache", "database", "network"
                            ],
                            "description": "Type of logs being analyzed"
                        },
                        "time_range": {
                            "type": "string",
                            "description": "Time range of the logs (optional)"
                        }
                    },
                    "required": ["logs"]
                }
            ),
            Tool(
                name="platform_engineering_advice",
                description="🏗️ Platform engineering and developer experience guidance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "challenge": {
                            "type": "string",
                            "description": "Platform engineering challenge or question"
                        },
                        "team_size": {
                            "type": "string",
                            "description": "Size of the development team"
                        },
                        "tech_stack": {
                            "type": "string",
                            "description": "Current technology stack"
                        }
                    },
                    "required": ["challenge"]
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls from Cursor."""
    try:
        if request.name == "analyze_devops_issue":
            result = await analyze_with_ollama(
                domain="devops",
                prompt=request.arguments["prompt"],
                context=request.arguments.get("context", ""),
                urgency=request.arguments.get("urgency", "medium")
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## 🔧 DevOps Analysis\n\n{result}\n\n---\n*Powered by InfraGenius*"
                )]
            )
        
        elif request.name == "analyze_sre_incident":
            result = await analyze_with_ollama(
                domain="sre",
                prompt=f"Incident: {request.arguments['incident']}",
                context=f"Severity: {request.arguments.get('severity', 'unknown')}, "
                       f"Affected Services: {request.arguments.get('affected_services', 'unknown')}",
                urgency=request.arguments.get("severity", "medium")
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## 🚨 SRE Incident Analysis\n\n{result}\n\n---\n*Powered by InfraGenius*"
                )]
            )
        
        elif request.name == "review_cloud_architecture":
            result = await analyze_with_ollama(
                domain="cloud",
                prompt=f"Architecture Review: {request.arguments['architecture']}",
                context=f"Cloud Provider: {request.arguments.get('cloud_provider', 'multi-cloud')}, "
                       f"Focus: {request.arguments.get('focus_area', 'general')}",
                urgency="medium"
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## ☁️ Cloud Architecture Review\n\n{result}\n\n---\n*Powered by InfraGenius*"
                )]
            )
        
        elif request.name == "generate_config":
            result = await analyze_with_ollama(
                domain="devops",
                prompt=f"Generate {request.arguments['tool']} configuration for: {request.arguments['requirements']}",
                context=f"Environment: {request.arguments.get('environment', 'production')}",
                urgency="low"
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## ⚙️ Configuration for {request.arguments['tool']}\n\n{result}\n\n---\n*Powered by InfraGenius*"
                )]
            )
        
        elif request.name == "explain_logs":
            result = await analyze_with_ollama(
                domain="devops",
                prompt=f"Analyze these logs: {request.arguments['logs']}",
                context=f"Log Type: {request.arguments.get('log_type', 'application')}, "
                       f"Time Range: {request.arguments.get('time_range', 'recent')}",
                urgency="medium"
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## 📋 Log Analysis\n\n{result}\n\n---\n*Powered by InfraGenius*"
                )]
            )
        
        elif request.name == "platform_engineering_advice":
            result = await analyze_with_ollama(
                domain="platform",
                prompt=f"Platform Engineering Challenge: {request.arguments['challenge']}",
                context=f"Team Size: {request.arguments.get('team_size', 'unknown')}, "
                       f"Tech Stack: {request.arguments.get('tech_stack', 'unknown')}",
                urgency="medium"
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"## 🏗️ Platform Engineering Advice\n\n{result}\n\n---\n*Powered by InfraGenius*"
                )]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {request.name}"
                )],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Error handling tool call: {e}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ Error: {str(e)}"
            )],
            isError=True
        )

@server.list_prompts()
async def handle_list_prompts() -> ListPromptsResult:
    """List available prompts for Cursor."""
    return ListPromptsResult(
        prompts=[
            Prompt(
                name="devops_expert",
                description="🔧 DevOps expert system prompt",
                arguments=[
                    PromptArgument(
                        name="issue",
                        description="The DevOps issue to analyze",
                        required=True
                    )
                ]
            ),
            Prompt(
                name="sre_incident_commander",
                description="🚨 SRE incident commander prompt",
                arguments=[
                    PromptArgument(
                        name="incident",
                        description="Description of the incident",
                        required=True
                    )
                ]
            ),
            Prompt(
                name="cloud_architect",
                description="☁️ Cloud architect consultant prompt",
                arguments=[
                    PromptArgument(
                        name="architecture",
                        description="Architecture to review",
                        required=True
                    )
                ]
            )
        ]
    )

@server.get_prompt()
async def handle_get_prompt(request: GetPromptRequest) -> GetPromptResult:
    """Handle prompt requests from Cursor."""
    if request.name == "devops_expert":
        issue = request.arguments.get("issue", "")
        
        return GetPromptResult(
            description="DevOps expert analysis prompt",
            messages=[
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text=f"""You are a Senior DevOps Engineer with 10+ years of experience in:
- CI/CD pipelines and automation
- Infrastructure as Code (Terraform, CloudFormation, Pulumi)
- Container orchestration (Kubernetes, Docker Swarm)
- Cloud platforms (AWS, Azure, GCP)
- Monitoring and observability
- Security and compliance

Analyze this DevOps issue and provide:
1. **Root Cause Analysis**: What's likely causing this issue?
2. **Immediate Actions**: What should be done right now?
3. **Long-term Solutions**: How to prevent this in the future?
4. **Best Practices**: Relevant DevOps best practices
5. **Tools & Resources**: Recommended tools and documentation

Issue: {issue}

Provide a comprehensive, actionable response with specific commands and configurations where applicable."""
                    )
                )
            ]
        )
    
    elif request.name == "sre_incident_commander":
        incident = request.arguments.get("incident", "")
        
        return GetPromptResult(
            description="SRE incident commander prompt",
            messages=[
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text=f"""You are a Principal Site Reliability Engineer acting as Incident Commander for:

{incident}

Follow the incident response process:

1. **ASSESS** - Understand the scope and impact
2. **TRIAGE** - Determine severity and priority
3. **MITIGATE** - Immediate actions to reduce impact
4. **COMMUNICATE** - Status updates for stakeholders
5. **RESOLVE** - Steps to fully resolve the incident
6. **LEARN** - Post-incident review recommendations

Provide structured incident response guidance with:
- Severity assessment (P0-P4)
- Immediate action items with owners
- Communication plan
- Technical resolution steps
- Monitoring and validation
- Post-incident action items

Be concise but thorough - this is an active incident."""
                    )
                )
            ]
        )
    
    elif request.name == "cloud_architect":
        architecture = request.arguments.get("architecture", "")
        
        return GetPromptResult(
            description="Cloud architect consultant prompt",
            messages=[
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text=f"""You are a Principal Cloud Architect with expertise in:
- Multi-cloud and hybrid cloud strategies
- Cloud-native architecture patterns
- Security and compliance frameworks
- Cost optimization and FinOps
- Scalability and performance optimization
- Disaster recovery and business continuity

Review this architecture and provide:

1. **Architecture Assessment**
   - Strengths and weaknesses
   - Compliance with cloud best practices
   - Scalability and performance considerations

2. **Security Review**
   - Security vulnerabilities and risks
   - Recommended security controls
   - Compliance considerations

3. **Cost Optimization**
   - Cost optimization opportunities
   - Right-sizing recommendations
   - Reserved instance strategies

4. **Recommendations**
   - Priority improvements
   - Alternative approaches
   - Migration strategies

Architecture: {architecture}

Provide specific, actionable recommendations with implementation guidance."""
                    )
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {request.name}")

async def analyze_with_ollama(domain: str, prompt: str, context: str = "", urgency: str = "medium") -> str:
    """Analyze using Ollama with domain expertise."""
    try:
        import httpx
        
        # Domain-specific system prompts
        system_prompts = {
            "devops": """You are a Senior DevOps Engineer with extensive experience in CI/CD, infrastructure automation, containerization, and cloud platforms. Provide practical, actionable advice with specific commands and configurations.""",
            
            "sre": """You are a Principal Site Reliability Engineer with deep expertise in system reliability, incident response, monitoring, and service level objectives. Focus on operational excellence and reliability engineering practices.""",
            
            "cloud": """You are a Principal Cloud Architect with expertise in multi-cloud strategies, cloud-native patterns, security, and cost optimization. Provide architectural guidance and best practices.""",
            
            "platform": """You are a Staff Platform Engineer focused on developer experience, internal tooling, and platform engineering. Help teams build self-service platforms and improve developer productivity."""
        }
        
        system_prompt = system_prompts.get(domain, system_prompts["devops"])
        
        full_prompt = f"{system_prompt}\n\nContext: {context}\nUrgency: {urgency}\n\nQuestion: {prompt}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2048
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                return f"Error calling Ollama: {response.status_code} - {response.text}"
    
    except Exception as e:
        logger.error(f"Error analyzing with Ollama: {e}")
        return f"Error: {str(e)}"

async def main():
    """Main entry point for MCP server."""
    try:
        # Test Ollama connection
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code != 200:
                logger.error(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}")
                return
            
        logger.info(f"✅ Connected to Ollama at {OLLAMA_BASE_URL}")
        logger.info(f"🤖 Using model: {OLLAMA_MODEL}")
        
        # Run MCP server
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="infragenius",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )
    
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
