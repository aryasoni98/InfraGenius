#!/usr/bin/env python3
"""
Industry-Standard DevOps/SRE Tools Integration Module
Provides integrations with popular DevOps, SRE, Cloud, and Platform Engineering tools
"""

import asyncio
import json
import logging
import subprocess
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import requests
import base64
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """Standardized result format for tool operations"""
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    tool_name: str = ""

class BaseTool(ABC):
    """Base class for all tool integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """Execute a tool operation"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate tool configuration"""
        pass

class KubernetesTool(BaseTool):
    """Kubernetes cluster management and analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.kubeconfig_path = config.get('kubeconfig_path', '~/.kube/config')
        self.namespace = config.get('namespace', 'default')
    
    def validate_config(self) -> bool:
        """Validate Kubernetes configuration"""
        try:
            result = subprocess.run(['kubectl', 'version', '--client'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("kubectl not found in PATH")
            return False
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """Execute Kubernetes operations"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if operation == 'get_pods':
                return await self._get_pods(**kwargs)
            elif operation == 'get_services':
                return await self._get_services(**kwargs)
            elif operation == 'get_deployments':
                return await self._get_deployments(**kwargs)
            elif operation == 'get_logs':
                return await self._get_logs(**kwargs)
            elif operation == 'get_events':
                return await self._get_events(**kwargs)
            elif operation == 'describe_resource':
                return await self._describe_resource(**kwargs)
            elif operation == 'get_resource_usage':
                return await self._get_resource_usage(**kwargs)
            elif operation == 'check_cluster_health':
                return await self._check_cluster_health(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message=f"Unknown operation: {operation}",
                    tool_name=self.name
                )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time,
                tool_name=self.name
            )
    
    async def _get_pods(self, namespace: Optional[str] = None, **kwargs) -> ToolResult:
        """Get pod information"""
        ns = namespace or self.namespace
        cmd = ['kubectl', 'get', 'pods', '-n', ns, '-o', 'json']
        
        result = await self._run_kubectl_command(cmd)
        if result.success:
            pods_data = json.loads(result.data)
            parsed_pods = []
            
            for pod in pods_data.get('items', []):
                pod_info = {
                    'name': pod['metadata']['name'],
                    'namespace': pod['metadata']['namespace'],
                    'phase': pod['status']['phase'],
                    'ready': self._count_ready_containers(pod),
                    'restarts': self._count_restarts(pod),
                    'age': self._calculate_age(pod['metadata']['creationTimestamp']),
                    'node': pod['spec'].get('nodeName', 'Unknown')
                }
                parsed_pods.append(pod_info)
            
            result.data = parsed_pods
        
        return result
    
    async def _get_services(self, namespace: Optional[str] = None, **kwargs) -> ToolResult:
        """Get service information"""
        ns = namespace or self.namespace
        cmd = ['kubectl', 'get', 'services', '-n', ns, '-o', 'json']
        
        result = await self._run_kubectl_command(cmd)
        if result.success:
            services_data = json.loads(result.data)
            parsed_services = []
            
            for service in services_data.get('items', []):
                service_info = {
                    'name': service['metadata']['name'],
                    'namespace': service['metadata']['namespace'],
                    'type': service['spec']['type'],
                    'cluster_ip': service['spec'].get('clusterIP', 'None'),
                    'external_ip': service['status'].get('loadBalancer', {}).get('ingress', []),
                    'ports': service['spec'].get('ports', []),
                    'age': self._calculate_age(service['metadata']['creationTimestamp'])
                }
                parsed_services.append(service_info)
            
            result.data = parsed_services
        
        return result
    
    async def _get_deployments(self, namespace: Optional[str] = None, **kwargs) -> ToolResult:
        """Get deployment information"""
        ns = namespace or self.namespace
        cmd = ['kubectl', 'get', 'deployments', '-n', ns, '-o', 'json']
        
        result = await self._run_kubectl_command(cmd)
        if result.success:
            deployments_data = json.loads(result.data)
            parsed_deployments = []
            
            for deployment in deployments_data.get('items', []):
                deployment_info = {
                    'name': deployment['metadata']['name'],
                    'namespace': deployment['metadata']['namespace'],
                    'ready_replicas': deployment['status'].get('readyReplicas', 0),
                    'replicas': deployment['spec']['replicas'],
                    'updated_replicas': deployment['status'].get('updatedReplicas', 0),
                    'available_replicas': deployment['status'].get('availableReplicas', 0),
                    'age': self._calculate_age(deployment['metadata']['creationTimestamp'])
                }
                parsed_deployments.append(deployment_info)
            
            result.data = parsed_deployments
        
        return result
    
    async def _get_logs(self, pod_name: str, namespace: Optional[str] = None, 
                       container: Optional[str] = None, lines: int = 100, **kwargs) -> ToolResult:
        """Get pod logs"""
        ns = namespace or self.namespace
        cmd = ['kubectl', 'logs', pod_name, '-n', ns, '--tail', str(lines)]
        
        if container:
            cmd.extend(['-c', container])
        
        return await self._run_kubectl_command(cmd)
    
    async def _get_events(self, namespace: Optional[str] = None, **kwargs) -> ToolResult:
        """Get cluster events"""
        ns = namespace or self.namespace
        cmd = ['kubectl', 'get', 'events', '-n', ns, '--sort-by=.metadata.creationTimestamp', '-o', 'json']
        
        result = await self._run_kubectl_command(cmd)
        if result.success:
            events_data = json.loads(result.data)
            parsed_events = []
            
            for event in events_data.get('items', []):
                event_info = {
                    'type': event.get('type', 'Normal'),
                    'reason': event.get('reason', 'Unknown'),
                    'message': event.get('message', ''),
                    'object': event.get('involvedObject', {}).get('name', 'Unknown'),
                    'object_kind': event.get('involvedObject', {}).get('kind', 'Unknown'),
                    'first_timestamp': event.get('firstTimestamp', ''),
                    'last_timestamp': event.get('lastTimestamp', ''),
                    'count': event.get('count', 1)
                }
                parsed_events.append(event_info)
            
            result.data = parsed_events
        
        return result
    
    async def _describe_resource(self, resource_type: str, resource_name: str, 
                                namespace: Optional[str] = None, **kwargs) -> ToolResult:
        """Describe a Kubernetes resource"""
        ns = namespace or self.namespace
        cmd = ['kubectl', 'describe', resource_type, resource_name, '-n', ns]
        
        return await self._run_kubectl_command(cmd)
    
    async def _get_resource_usage(self, **kwargs) -> ToolResult:
        """Get resource usage metrics"""
        # Get node metrics
        node_cmd = ['kubectl', 'top', 'nodes']
        node_result = await self._run_kubectl_command(node_cmd)
        
        # Get pod metrics
        pod_cmd = ['kubectl', 'top', 'pods', '--all-namespaces']
        pod_result = await self._run_kubectl_command(pod_cmd)
        
        if node_result.success and pod_result.success:
            return ToolResult(
                success=True,
                data={
                    'nodes': node_result.data,
                    'pods': pod_result.data
                },
                tool_name=self.name
            )
        else:
            return ToolResult(
                success=False,
                data=None,
                error_message="Failed to get resource usage metrics",
                tool_name=self.name
            )
    
    async def _check_cluster_health(self, **kwargs) -> ToolResult:
        """Check overall cluster health"""
        health_checks = {}
        
        # Check cluster info
        cluster_cmd = ['kubectl', 'cluster-info']
        cluster_result = await self._run_kubectl_command(cluster_cmd)
        health_checks['cluster_info'] = cluster_result.success
        
        # Check node status
        nodes_cmd = ['kubectl', 'get', 'nodes', '-o', 'json']
        nodes_result = await self._run_kubectl_command(nodes_cmd)
        if nodes_result.success:
            nodes_data = json.loads(nodes_result.data)
            healthy_nodes = 0
            total_nodes = len(nodes_data.get('items', []))
            
            for node in nodes_data.get('items', []):
                conditions = node.get('status', {}).get('conditions', [])
                for condition in conditions:
                    if condition.get('type') == 'Ready' and condition.get('status') == 'True':
                        healthy_nodes += 1
                        break
            
            health_checks['nodes'] = {
                'healthy': healthy_nodes,
                'total': total_nodes,
                'status': 'healthy' if healthy_nodes == total_nodes else 'degraded'
            }
        
        # Check system pods
        system_cmd = ['kubectl', 'get', 'pods', '-n', 'kube-system', '-o', 'json']
        system_result = await self._run_kubectl_command(system_cmd)
        if system_result.success:
            system_data = json.loads(system_result.data)
            running_pods = 0
            total_pods = len(system_data.get('items', []))
            
            for pod in system_data.get('items', []):
                if pod.get('status', {}).get('phase') == 'Running':
                    running_pods += 1
            
            health_checks['system_pods'] = {
                'running': running_pods,
                'total': total_pods,
                'status': 'healthy' if running_pods == total_pods else 'degraded'
            }
        
        overall_health = all(
            check.get('status', True) == 'healthy' if isinstance(check, dict) else check
            for check in health_checks.values()
        )
        
        return ToolResult(
            success=True,
            data={
                'overall_health': 'healthy' if overall_health else 'degraded',
                'checks': health_checks
            },
            tool_name=self.name
        )
    
    async def _run_kubectl_command(self, cmd: List[str]) -> ToolResult:
        """Run a kubectl command"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    data=stdout.decode('utf-8').strip(),
                    execution_time=execution_time,
                    tool_name=self.name
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message=stderr.decode('utf-8').strip(),
                    execution_time=execution_time,
                    tool_name=self.name
                )
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                data=None,
                error_message="Command timed out",
                execution_time=30.0,
                tool_name=self.name
            )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time,
                tool_name=self.name
            )
    
    def _count_ready_containers(self, pod: Dict[str, Any]) -> str:
        """Count ready containers in a pod"""
        container_statuses = pod.get('status', {}).get('containerStatuses', [])
        ready_count = sum(1 for status in container_statuses if status.get('ready', False))
        total_count = len(container_statuses)
        return f"{ready_count}/{total_count}"
    
    def _count_restarts(self, pod: Dict[str, Any]) -> int:
        """Count total restarts for a pod"""
        container_statuses = pod.get('status', {}).get('containerStatuses', [])
        return sum(status.get('restartCount', 0) for status in container_statuses)
    
    def _calculate_age(self, creation_timestamp: str) -> str:
        """Calculate age from creation timestamp"""
        try:
            creation_time = datetime.fromisoformat(creation_timestamp.replace('Z', '+00:00'))
            age = datetime.now(creation_time.tzinfo) - creation_time
            
            if age.days > 0:
                return f"{age.days}d"
            elif age.seconds > 3600:
                return f"{age.seconds // 3600}h"
            elif age.seconds > 60:
                return f"{age.seconds // 60}m"
            else:
                return f"{age.seconds}s"
        except Exception:
            return "Unknown"

class PrometheusTool(BaseTool):
    """Prometheus metrics collection and analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoint = config.get('endpoint', 'http://localhost:9090')
        self.timeout = config.get('timeout', 30)
    
    def validate_config(self) -> bool:
        """Validate Prometheus configuration"""
        try:
            response = requests.get(f"{self.endpoint}/api/v1/status/config", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """Execute Prometheus operations"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if operation == 'query':
                return await self._query(**kwargs)
            elif operation == 'query_range':
                return await self._query_range(**kwargs)
            elif operation == 'get_targets':
                return await self._get_targets(**kwargs)
            elif operation == 'get_alerts':
                return await self._get_alerts(**kwargs)
            elif operation == 'get_rules':
                return await self._get_rules(**kwargs)
            elif operation == 'get_metrics':
                return await self._get_metrics(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message=f"Unknown operation: {operation}",
                    tool_name=self.name
                )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time,
                tool_name=self.name
            )
    
    async def _query(self, query: str, time: Optional[str] = None, **kwargs) -> ToolResult:
        """Execute Prometheus query"""
        params = {'query': query}
        if time:
            params['time'] = time
        
        return await self._make_request('/api/v1/query', params)
    
    async def _query_range(self, query: str, start: str, end: str, step: str, **kwargs) -> ToolResult:
        """Execute Prometheus range query"""
        params = {
            'query': query,
            'start': start,
            'end': end,
            'step': step
        }
        
        return await self._make_request('/api/v1/query_range', params)
    
    async def _get_targets(self, **kwargs) -> ToolResult:
        """Get Prometheus targets"""
        return await self._make_request('/api/v1/targets')
    
    async def _get_alerts(self, **kwargs) -> ToolResult:
        """Get active alerts"""
        return await self._make_request('/api/v1/alerts')
    
    async def _get_rules(self, **kwargs) -> ToolResult:
        """Get alerting and recording rules"""
        return await self._make_request('/api/v1/rules')
    
    async def _get_metrics(self, **kwargs) -> ToolResult:
        """Get available metrics"""
        return await self._make_request('/api/v1/label/__name__/values')
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> ToolResult:
        """Make HTTP request to Prometheus"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    f"{self.endpoint}{endpoint}",
                    params=params,
                    timeout=self.timeout
                )
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if response.status_code == 200:
                return ToolResult(
                    success=True,
                    data=response.json(),
                    execution_time=execution_time,
                    tool_name=self.name
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message=f"HTTP {response.status_code}: {response.text}",
                    execution_time=execution_time,
                    tool_name=self.name
                )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time,
                tool_name=self.name
            )

class TerraformTool(BaseTool):
    """Terraform infrastructure management"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.working_directory = config.get('working_directory', '.')
        self.terraform_binary = config.get('terraform_binary', 'terraform')
    
    def validate_config(self) -> bool:
        """Validate Terraform configuration"""
        try:
            result = subprocess.run([self.terraform_binary, 'version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("terraform not found in PATH")
            return False
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """Execute Terraform operations"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if operation == 'plan':
                return await self._plan(**kwargs)
            elif operation == 'apply':
                return await self._apply(**kwargs)
            elif operation == 'destroy':
                return await self._destroy(**kwargs)
            elif operation == 'validate':
                return await self._validate(**kwargs)
            elif operation == 'fmt':
                return await self._fmt(**kwargs)
            elif operation == 'show':
                return await self._show(**kwargs)
            elif operation == 'state_list':
                return await self._state_list(**kwargs)
            elif operation == 'output':
                return await self._output(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message=f"Unknown operation: {operation}",
                    tool_name=self.name
                )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time,
                tool_name=self.name
            )
    
    async def _plan(self, var_file: Optional[str] = None, **kwargs) -> ToolResult:
        """Run terraform plan"""
        cmd = [self.terraform_binary, 'plan', '-no-color']
        if var_file:
            cmd.extend(['-var-file', var_file])
        
        return await self._run_terraform_command(cmd)
    
    async def _apply(self, var_file: Optional[str] = None, auto_approve: bool = False, **kwargs) -> ToolResult:
        """Run terraform apply"""
        cmd = [self.terraform_binary, 'apply', '-no-color']
        if var_file:
            cmd.extend(['-var-file', var_file])
        if auto_approve:
            cmd.append('-auto-approve')
        
        return await self._run_terraform_command(cmd)
    
    async def _destroy(self, var_file: Optional[str] = None, auto_approve: bool = False, **kwargs) -> ToolResult:
        """Run terraform destroy"""
        cmd = [self.terraform_binary, 'destroy', '-no-color']
        if var_file:
            cmd.extend(['-var-file', var_file])
        if auto_approve:
            cmd.append('-auto-approve')
        
        return await self._run_terraform_command(cmd)
    
    async def _validate(self, **kwargs) -> ToolResult:
        """Run terraform validate"""
        cmd = [self.terraform_binary, 'validate']
        return await self._run_terraform_command(cmd)
    
    async def _fmt(self, **kwargs) -> ToolResult:
        """Run terraform fmt"""
        cmd = [self.terraform_binary, 'fmt', '-diff']
        return await self._run_terraform_command(cmd)
    
    async def _show(self, **kwargs) -> ToolResult:
        """Run terraform show"""
        cmd = [self.terraform_binary, 'show', '-json']
        return await self._run_terraform_command(cmd)
    
    async def _state_list(self, **kwargs) -> ToolResult:
        """Run terraform state list"""
        cmd = [self.terraform_binary, 'state', 'list']
        return await self._run_terraform_command(cmd)
    
    async def _output(self, **kwargs) -> ToolResult:
        """Run terraform output"""
        cmd = [self.terraform_binary, 'output', '-json']
        return await self._run_terraform_command(cmd)
    
    async def _run_terraform_command(self, cmd: List[str]) -> ToolResult:
        """Run a terraform command"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_directory
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            execution_time = asyncio.get_event_loop().time() - start_time
            
            output = stdout.decode('utf-8').strip()
            error = stderr.decode('utf-8').strip()
            
            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    data=output,
                    execution_time=execution_time,
                    tool_name=self.name
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error_message=error or output,
                    execution_time=execution_time,
                    tool_name=self.name
                )
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                data=None,
                error_message="Command timed out",
                execution_time=300.0,
                tool_name=self.name
            )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time,
                tool_name=self.name
            )

class IndustryToolsManager:
    """Manager for all industry tools"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all configured tools"""
        tool_classes = {
            'kubernetes': KubernetesTool,
            'prometheus': PrometheusTool,
            'terraform': TerraformTool,
        }
        
        for tool_name, tool_config in self.config.get('integrations', {}).items():
            if tool_config.get('enabled', False) and tool_name in tool_classes:
                try:
                    tool_instance = tool_classes[tool_name](tool_config)
                    if tool_instance.validate_config():
                        self.tools[tool_name] = tool_instance
                        logger.info(f"Initialized {tool_name} tool")
                    else:
                        logger.warning(f"Failed to validate {tool_name} configuration")
                except Exception as e:
                    logger.error(f"Failed to initialize {tool_name} tool: {e}")
    
    async def execute_tool_operation(self, tool_name: str, operation: str, **kwargs) -> ToolResult:
        """Execute operation on a specific tool"""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                data=None,
                error_message=f"Tool '{tool_name}' not available or not configured",
                tool_name=tool_name
            )
        
        return await self.tools[tool_name].execute(operation, **kwargs)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        return {
            'name': tool.name,
            'config': tool.config,
            'validated': tool.validate_config()
        }
