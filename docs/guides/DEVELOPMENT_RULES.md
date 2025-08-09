# 🛠️ Development Rules & Best Practices

This document outlines the development rules, standards, and best practices for contributing to InfraGenius.

## 📋 Table of Contents

- [Code Standards](#code-standards)
- [Git Workflow](#git-workflow)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Security Guidelines](#security-guidelines)
- [Performance Standards](#performance-standards)
- [Review Process](#review-process)

---

## 🎯 Code Standards

### Python Code Style

#### 1. **Formatting and Linting**

**Required Tools:**
- **Black** (code formatting)
- **isort** (import sorting)  
- **flake8** (linting)
- **mypy** (type checking)

**Configuration:**
```bash
# Format code
black --line-length 88 .
isort --profile black .

# Lint code
flake8 --max-line-length 88 --extend-ignore E203,W503 .
mypy mcp_server/ --strict
```

#### 2. **Code Structure**

**File Organization:**
```python
#!/usr/bin/env python3
"""Module docstring describing purpose and usage.

This module provides functionality for...

Example:
    Basic usage example:
    
    >>> from mcp_server.core import Analyzer
    >>> analyzer = Analyzer()
    >>> result = analyzer.analyze("issue")
"""

# Standard library imports
import asyncio
import logging
import os
from typing import Dict, List, Optional, Union

# Third-party imports
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Local imports
from mcp_server.core.config import Config
from mcp_server.utils.logger import get_logger

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Module-level logger
logger = get_logger(__name__)
```

#### 3. **Type Hints**

**Required for all functions:**
```python
from typing import Any, Dict, List, Optional, Union

def analyze_issue(
    prompt: str,
    domain: str = "devops",
    context: Optional[str] = None,
    options: Dict[str, Any] = None
) -> Dict[str, Union[str, List[str]]]:
    """Analyze DevOps/SRE issue with AI.
    
    Args:
        prompt: The issue description to analyze.
        domain: Domain expertise (devops, sre, cloud, platform).
        context: Additional context about the environment.
        options: Additional analysis options.
    
    Returns:
        Dictionary containing analysis results and recommendations.
    
    Raises:
        ValueError: If prompt is empty or invalid domain.
        HTTPException: If API request fails.
    """
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    # Implementation here...
    return {
        "analysis": "...",
        "recommendations": ["..."],
        "confidence": 0.95
    }
```

#### 4. **Error Handling**

**Structured Error Handling:**
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class InfraGeniusError(Exception):
    """Base exception for InfraGenius."""
    pass

class AnalysisError(InfraGeniusError):
    """Raised when analysis fails."""
    pass

class ConfigurationError(InfraGeniusError):
    """Raised when configuration is invalid."""
    pass

def safe_analysis(prompt: str) -> Optional[Dict[str, Any]]:
    """Safely perform analysis with proper error handling."""
    try:
        result = perform_analysis(prompt)
        logger.info("Analysis completed successfully", extra={
            "prompt_length": len(prompt),
            "result_keys": list(result.keys())
        })
        return result
    
    except AnalysisError as e:
        logger.error("Analysis failed", extra={
            "error": str(e),
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt
        })
        return None
    
    except Exception as e:
        logger.exception("Unexpected error during analysis", extra={
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        raise AnalysisError(f"Analysis failed: {e}") from e
```

#### 5. **Logging Standards**

**Structured Logging:**
```python
import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)

def process_request(request_id: str, data: Dict[str, Any]) -> None:
    """Process incoming request with structured logging."""
    logger.info(
        "Processing request",
        request_id=request_id,
        data_size=len(str(data)),
        timestamp=datetime.utcnow().isoformat()
    )
    
    try:
        # Process request
        result = process_data(data)
        
        logger.info(
            "Request processed successfully",
            request_id=request_id,
            result_size=len(str(result)),
            processing_time=time.time() - start_time
        )
    
    except Exception as e:
        logger.error(
            "Request processing failed",
            request_id=request_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise
```

---

## 🔄 Git Workflow

### Branch Strategy

**Branch Types:**
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Critical production fixes
- `docs/*` - Documentation updates

**Branch Naming:**
```bash
# Feature branches
feature/add-kubernetes-analysis
feature/improve-caching-performance
feature/cursor-mcp-integration

# Bug fix branches
fix/memory-leak-analyzer
fix/config-validation-error
fix/docker-build-issue

# Documentation branches
docs/update-api-reference
docs/add-deployment-guide
docs/fix-typos-readme
```

### Commit Standards

**Conventional Commits:**
```bash
# Format: type(scope): description

# Types:
feat:     # New feature
fix:      # Bug fix
docs:     # Documentation changes
style:    # Code style changes (formatting, etc.)
refactor: # Code refactoring
test:     # Adding or updating tests
chore:    # Maintenance tasks
perf:     # Performance improvements
ci:       # CI/CD changes
build:    # Build system changes

# Examples:
feat(analyzer): add support for Kubernetes log analysis
fix(config): resolve validation error for missing fields
docs(api): update REST API documentation
test(integration): add tests for Ollama integration
refactor(core): simplify error handling logic
perf(cache): optimize memory usage in caching layer
```

**Commit Message Structure:**
```
feat(analyzer): add support for Kubernetes log analysis

- Implement Kubernetes-specific log parsing
- Add pod crash analysis capabilities
- Include resource usage recommendations
- Update tests and documentation

Closes #123
Co-authored-by: Jane Doe <jane@example.com>
```

### Pull Request Process

**PR Title Format:**
```
feat: add Kubernetes log analysis support
fix: resolve memory leak in analyzer
docs: update local development guide
```

**PR Description Template:**
```markdown
## 🎯 Description
Brief description of changes made.

## 🔗 Related Issues
- Fixes #123
- Relates to #456

## 🧪 Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## ✅ Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Added new tests for changes

## 📝 Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] No new warnings or errors
```

---

## 🧪 Testing Requirements

### Testing Standards

**Coverage Requirements:**
- **Minimum**: 80% overall coverage
- **Critical paths**: 95% coverage
- **New features**: 90% coverage

**Test Types:**
1. **Unit Tests** - Test individual functions/classes
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Performance Tests** - Test performance characteristics

### Test Structure

**Directory Organization:**
```
tests/
├── unit/
│   ├── test_analyzer.py
│   ├── test_config.py
│   └── test_utils.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_ollama_integration.py
│   └── test_database.py
├── performance/
│   ├── test_response_times.py
│   └── test_memory_usage.py
├── fixtures/
│   ├── sample_configs.py
│   └── mock_responses.py
└── conftest.py
```

**Test Implementation:**
```python
import pytest
from unittest.mock import AsyncMock, Mock, patch

from mcp_server.core.analyzer import Analyzer
from mcp_server.core.config import Config

class TestAnalyzer:
    """Test cases for Analyzer class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config({
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "gpt-oss:latest"
            }
        })
    
    @pytest.fixture
    def analyzer(self, config):
        """Create analyzer instance."""
        return Analyzer(config)
    
    @pytest.mark.asyncio
    async def test_analyze_devops_issue_success(self, analyzer):
        """Test successful DevOps issue analysis."""
        # Arrange
        prompt = "Kubernetes pods are crashing"
        expected_result = {
            "analysis": "Pod crash analysis...",
            "recommendations": ["Check resource limits", "Review logs"]
        }
        
        with patch.object(analyzer, '_call_ollama') as mock_call:
            mock_call.return_value = expected_result
            
            # Act
            result = await analyzer.analyze(prompt, domain="devops")
            
            # Assert
            assert result["analysis"] is not None
            assert len(result["recommendations"]) > 0
            mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_invalid_domain(self, analyzer):
        """Test analysis with invalid domain."""
        with pytest.raises(ValueError, match="Invalid domain"):
            await analyzer.analyze("test prompt", domain="invalid")
    
    @pytest.mark.parametrize("domain,expected_expertise", [
        ("devops", "senior"),
        ("sre", "principal"),
        ("cloud", "architect"),
        ("platform", "staff")
    ])
    def test_get_domain_expertise(self, analyzer, domain, expected_expertise):
        """Test domain expertise mapping."""
        expertise = analyzer.get_domain_expertise(domain)
        assert expertise == expected_expertise
```

### Performance Testing

**Response Time Requirements:**
```python
import pytest
import time
from mcp_server.core.analyzer import Analyzer

class TestPerformance:
    """Performance test cases."""
    
    @pytest.mark.performance
    async def test_analysis_response_time(self, analyzer):
        """Test analysis response time is under 2 seconds."""
        start_time = time.time()
        
        result = await analyzer.analyze(
            "Test prompt for performance",
            domain="devops"
        )
        
        response_time = time.time() - start_time
        
        assert response_time < 2.0, f"Response time {response_time}s exceeds 2s limit"
        assert result is not None
    
    @pytest.mark.performance
    async def test_concurrent_requests(self, analyzer):
        """Test handling of concurrent requests."""
        import asyncio
        
        tasks = []
        for i in range(10):
            task = analyzer.analyze(f"Concurrent test {i}", domain="devops")
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        assert total_time < 5.0, f"Concurrent requests took {total_time}s"
        assert len(results) == 10
        assert all(r is not None for r in results)
```

---

## 📚 Documentation Standards

### Code Documentation

**Docstring Format (Google Style):**
```python
def analyze_infrastructure(
    config: Dict[str, Any],
    environment: str = "production",
    include_recommendations: bool = True
) -> InfrastructureAnalysis:
    """Analyze infrastructure configuration for issues and optimizations.
    
    This function performs comprehensive analysis of infrastructure configuration
    including security, performance, and cost optimization recommendations.
    
    Args:
        config: Infrastructure configuration dictionary containing resources,
            networking, and security settings.
        environment: Target environment for analysis. Must be one of
            'development', 'staging', or 'production'. Defaults to 'production'.
        include_recommendations: Whether to include optimization recommendations
            in the analysis result. Defaults to True.
    
    Returns:
        InfrastructureAnalysis object containing:
            - issues: List of identified issues with severity levels
            - recommendations: List of optimization recommendations
            - score: Overall infrastructure health score (0-100)
            - metadata: Additional analysis metadata
    
    Raises:
        ValueError: If config is empty or environment is invalid.
        AnalysisError: If analysis fails due to configuration issues.
        TimeoutError: If analysis takes longer than configured timeout.
    
    Example:
        >>> config = {
        ...     "compute": {"instances": [...]},
        ...     "networking": {"vpc": {...}},
        ...     "security": {"groups": [...]}
        ... }
        >>> analysis = analyze_infrastructure(config, "production")
        >>> print(f"Health score: {analysis.score}")
        Health score: 87
        >>> for issue in analysis.issues:
        ...     print(f"- {issue.description} (severity: {issue.severity})")
    
    Note:
        This function may take several seconds for large configurations.
        Consider using async version for better performance in web applications.
    """
    # Implementation here...
```

### API Documentation

**OpenAPI/Swagger Documentation:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="InfraGenius API",
    description="AI-Powered DevOps & SRE Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""
    
    prompt: str = Field(
        ...,
        description="The issue or question to analyze",
        example="My Kubernetes pods are crashing with OOMKilled errors",
        min_length=10,
        max_length=5000
    )
    domain: str = Field(
        "devops",
        description="Domain expertise to use for analysis",
        example="devops",
        regex="^(devops|sre|cloud|platform)$"
    )
    context: Optional[str] = Field(
        None,
        description="Additional context about your environment",
        example="Production cluster on AWS EKS with 100+ microservices",
        max_length=1000
    )
    urgency: Optional[str] = Field(
        "medium",
        description="Issue urgency level",
        example="high",
        regex="^(low|medium|high|critical)$"
    )

@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze DevOps/SRE Issue",
    description="""
    Analyze DevOps, SRE, Cloud, or Platform Engineering issues using AI.
    
    This endpoint provides comprehensive analysis including:
    - Root cause identification
    - Step-by-step resolution guidance
    - Best practices recommendations
    - Prevention strategies
    
    **Rate Limits:**
    - 100 requests per minute for authenticated users
    - 10 requests per minute for anonymous users
    
    **Response Time:**
    - Typical: 1-3 seconds
    - Complex issues: up to 10 seconds
    """,
    tags=["Analysis"],
    responses={
        200: {"description": "Analysis completed successfully"},
        400: {"description": "Invalid request parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_issue(request: AnalysisRequest):
    """Analyze DevOps/SRE issue with AI expertise."""
    # Implementation here...
```

---

## 🔒 Security Guidelines

### Security Standards

**1. Input Validation**
```python
from pydantic import BaseModel, Field, validator
import re

class SecureAnalysisRequest(BaseModel):
    """Secure request model with validation."""
    
    prompt: str = Field(..., min_length=1, max_length=10000)
    domain: str = Field(..., regex="^(devops|sre|cloud|platform)$")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate and sanitize prompt input."""
        # Remove potential injection patterns
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'exec\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Potentially dangerous content detected")
        
        # Sanitize input
        v = v.strip()
        v = re.sub(r'[<>"\']', '', v)  # Remove HTML/JS characters
        
        return v

    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain parameter."""
        allowed_domains = {'devops', 'sre', 'cloud', 'platform'}
        if v not in allowed_domains:
            raise ValueError(f"Domain must be one of {allowed_domains}")
        return v
```

**2. Secret Management**
```python
import os
from typing import Optional

class SecretManager:
    """Secure secret management."""
    
    @staticmethod
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variables."""
        # Try environment variables first
        value = os.getenv(key, default)
        
        # Validate secret format if needed
        if key.endswith('_API_KEY') and value:
            if len(value) < 20:
                raise ValueError(f"Invalid API key format for {key}")
        
        return value
    
    @staticmethod
    def mask_secret(secret: str, visible_chars: int = 4) -> str:
        """Mask secret for logging."""
        if not secret or len(secret) <= visible_chars * 2:
            return "*" * 8
        
        return secret[:visible_chars] + "*" * (len(secret) - visible_chars * 2) + secret[-visible_chars:]

# Usage
api_key = SecretManager.get_secret('OPENAI_API_KEY')
logger.info(f"Using API key: {SecretManager.mask_secret(api_key)}")
```

**3. Rate Limiting**
```python
from functools import wraps
from time import time
from collections import defaultdict

class RateLimiter:
    """Simple rate limiting implementation."""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed."""
        now = time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """Rate limiting decorator."""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get identifier (IP, user ID, etc.)
            identifier = get_request_identifier()
            
            if not limiter.is_allowed(identifier):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## ⚡ Performance Standards

### Response Time Requirements

| Endpoint | Target | Maximum |
|----------|--------|---------|
| `/health` | < 50ms | 100ms |
| `/analyze` | < 2s | 10s |
| `/generate` | < 3s | 15s |
| `/explain` | < 1s | 5s |

### Memory Usage

**Memory Management:**
```python
import psutil
import gc
from functools import wraps

def monitor_memory(func):
    """Monitor memory usage of function."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get memory before
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = await func(*args, **kwargs)
            
            # Get memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            # Log if significant memory usage
            if memory_used > 100:  # More than 100MB
                logger.warning(
                    f"High memory usage in {func.__name__}",
                    memory_used_mb=memory_used,
                    memory_total_mb=memory_after
                )
            
            # Force garbage collection for large operations
            if memory_used > 500:  # More than 500MB
                gc.collect()
            
            return result
            
        except Exception as e:
            # Cleanup on error
            gc.collect()
            raise
    
    return wrapper
```

### Caching Strategy

**Intelligent Caching:**
```python
import hashlib
import json
from functools import wraps
from typing import Any, Dict, Optional

class IntelligentCache:
    """Intelligent caching with TTL and LRU eviction."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function call."""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check TTL
        if time.time() > entry['expires']:
            del self.cache[key]
            del self.access_times[key]
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        
        # Evict LRU if at capacity
        if len(self.cache) >= self.max_size:
            lru_key = min(self.access_times.keys(), key=self.access_times.get)
            del self.cache[lru_key]
            del self.access_times[lru_key]
        
        self.cache[key] = {
            'value': value,
            'expires': time.time() + ttl,
            'created': time.time()
        }
        self.access_times[key] = time.time()

# Global cache instance
cache = IntelligentCache()

def cached(ttl: int = 3600):
    """Caching decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        return wrapper
    return decorator
```

---

## 👥 Review Process

### Code Review Checklist

**For Authors:**
- [ ] Code follows style guidelines (Black, isort, flake8)
- [ ] All functions have type hints and docstrings
- [ ] Tests added/updated with 80%+ coverage
- [ ] Documentation updated (API docs, README, etc.)
- [ ] No hardcoded secrets or credentials
- [ ] Error handling implemented properly
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Breaking changes documented

**For Reviewers:**
- [ ] Code is readable and maintainable
- [ ] Logic is correct and efficient
- [ ] Tests adequately cover changes
- [ ] Documentation is clear and complete
- [ ] Security best practices followed
- [ ] Performance is acceptable
- [ ] Error handling is comprehensive
- [ ] Code follows established patterns

### Review Guidelines

**1. Focus Areas:**
- **Correctness**: Does the code do what it's supposed to do?
- **Security**: Are there any security vulnerabilities?
- **Performance**: Will this impact system performance?
- **Maintainability**: Is the code easy to understand and modify?
- **Testing**: Are there adequate tests?

**2. Review Comments:**
```
# Good review comments:
"Consider using a more specific exception type here for better error handling."

"This function could benefit from caching since it's called frequently."

"Great implementation! The error handling is comprehensive."

"Could you add a docstring example for this complex function?"

# Avoid:
"This is wrong." (not specific)
"Change this." (no explanation)
"I don't like this." (not constructive)
```

**3. Approval Criteria:**
- All CI checks pass
- At least one approving review from maintainer
- No unresolved conversations
- Documentation updated
- Tests pass with adequate coverage

---

## 🚀 Deployment Rules

### Environment Promotion

**Promotion Path:**
```
Local Development → Test → Staging → Production
```

**Requirements per Environment:**
- **Test**: All tests pass, code review approved
- **Staging**: Integration tests pass, performance tests pass
- **Production**: Staging deployment successful, monitoring in place

### Release Process

**Version Numbering (SemVer):**
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**Release Checklist:**
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] Deployment tested
- [ ] Rollback plan ready
- [ ] Monitoring alerts configured

---

## 📞 Getting Help

If you have questions about these development rules:

1. **Check Documentation**: Review existing docs and examples
2. **Ask in Discussions**: Use GitHub Discussions for questions
3. **Join Discord**: Real-time help in our Discord server
4. **Create Issue**: For clarifications or rule suggestions

**Remember**: These rules exist to maintain code quality and ensure a smooth development experience for everyone. When in doubt, ask for help! 🤝
