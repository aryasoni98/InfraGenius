# Contributing to InfraGenius

First off, thank you for considering contributing to InfraGenius! 🎉 

It's people like you that make InfraGenius such a great tool for the DevOps and SRE community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Workflow](#development-workflow)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@infragenius.ai](mailto:conduct@infragenius.ai).

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://python.org)
- **Docker** - [Install Docker](https://docker.com)
- **Git** - [Install Git](https://git-scm.com)
- **Ollama** - [Install Ollama](https://ollama.ai)

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/infragenius.git
   cd infragenius
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Configure your environment**
   ```bash
   # Copy example configuration
   cp mcp_server/config.json.example mcp_server/config.json
   
   # Edit configuration as needed
   nano mcp_server/config.json
   ```

4. **Start development services**
   ```bash
   # Start Ollama service
   ollama serve
   
   # In another terminal, pull required models
   ollama pull gpt-oss:latest
   
   # Start the development server
   python mcp_server/server.py
   ```

5. **Verify setup**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black --check .
   flake8 .
   
   # Run security checks
   bandit -r mcp_server/
   ```

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the [issue list](https://github.com/infragenius/infragenius/issues) as you might find that the problem has already been reported.

When creating a bug report, please include:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots and animated GIFs if possible**
- **Include your environment details**:
  - OS version
  - Python version
  - Docker version
  - Ollama version
  - InfraGenius version

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful to most InfraGenius users**
- **List some other tools where this enhancement exists**

### 🔧 Contributing Code

#### Types of Contributions

1. **Bug Fixes** - Fix reported issues
2. **Features** - Add new functionality
3. **Performance** - Improve performance and efficiency
4. **Documentation** - Improve or add documentation
5. **Tests** - Add or improve test coverage
6. **DevOps** - Improve CI/CD, deployment, or infrastructure

#### Before You Start

1. **Check existing issues** - Look for related issues or feature requests
2. **Create an issue** - If none exists, create one to discuss your changes
3. **Get feedback** - Wait for maintainer feedback before starting large changes
4. **Claim the issue** - Comment that you're working on it

## 🔄 Development Workflow

### 1. Create a Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 2. Make Your Changes

- Write clear, readable code
- Follow the style guidelines below
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run the full test suite
pytest

# Run specific tests
pytest tests/test_server.py

# Run with coverage
pytest --cov=mcp_server --cov-report=html

# Run integration tests
pytest tests/integration/

# Run performance tests
pytest tests/performance/
```

### 4. Commit Your Changes

We use [Conventional Commits](https://conventionalcommits.org/) for commit messages:

```bash
# Examples of good commit messages
git commit -m "feat: add support for Azure cost optimization"
git commit -m "fix: resolve memory leak in caching layer"
git commit -m "docs: update API documentation for new endpoints"
git commit -m "test: add integration tests for Kubernetes plugin"
git commit -m "refactor: simplify authentication middleware"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

## 📝 Style Guidelines

### Python Code Style

We follow [PEP 8](https://pep8.org/) with some additional guidelines:

#### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check style with flake8
flake8 .
```

#### Code Quality

- **Line length**: 88 characters (Black default)
- **Imports**: Use absolute imports, group with isort
- **Docstrings**: Use Google style docstrings
- **Type hints**: Use type hints for all public functions
- **Error handling**: Use specific exception types
- **Logging**: Use structured logging with appropriate levels

#### Example Code Structure

```python
"""Module docstring describing the purpose."""

import logging
import sys
from typing import Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from mcp_server.core import BaseServer
from mcp_server.utils import validate_input

logger = logging.getLogger(__name__)


class ExampleModel(BaseModel):
    """Example Pydantic model with proper docstring.
    
    Attributes:
        name: The name of the example.
        value: The value associated with the example.
        optional_field: An optional field with default value.
    """
    
    name: str = Field(..., description="The name of the example")
    value: int = Field(..., ge=0, description="Non-negative integer value")
    optional_field: Optional[str] = Field(None, description="Optional string field")


class ExampleService:
    """Service class for handling example operations."""
    
    def __init__(self, config: Dict[str, Union[str, int]]) -> None:
        """Initialize the example service.
        
        Args:
            config: Configuration dictionary containing service settings.
        """
        self.config = config
        self._initialized = False
    
    async def process_example(
        self, 
        data: ExampleModel,
        context: Optional[str] = None
    ) -> Dict[str, Union[str, int]]:
        """Process example data and return results.
        
        Args:
            data: The example data to process.
            context: Optional context for processing.
            
        Returns:
            Dictionary containing processing results.
            
        Raises:
            ValueError: If data validation fails.
            RuntimeError: If service is not initialized.
        """
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        try:
            # Validate input
            validate_input(data.dict())
            
            # Process data
            result = {
                "status": "success",
                "processed_name": data.name.upper(),
                "processed_value": data.value * 2,
            }
            
            logger.info(
                "Successfully processed example",
                extra={"name": data.name, "value": data.value}
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to process example",
                extra={"error": str(e), "data": data.dict()}
            )
            raise ValueError(f"Processing failed: {e}") from e
```

### Documentation Style

#### README Files
- Use clear, descriptive headings
- Include code examples
- Add badges for build status, coverage, etc.
- Provide quick start instructions
- Include troubleshooting section

#### API Documentation
- Use OpenAPI/Swagger specifications
- Include request/response examples
- Document all parameters and return values
- Add authentication requirements
- Include error codes and messages

#### Code Comments
```python
# Good: Explain why, not what
# Cache results to avoid expensive API calls during peak hours
cache.set(key, result, ttl=3600)

# Bad: Explain what (obvious from code)
# Set cache with key, result, and TTL of 3600
cache.set(key, result, ttl=3600)
```

### Testing Guidelines

#### Test Structure
```python
"""Test module for example service."""

import pytest
from unittest.mock import Mock, patch

from mcp_server.services.example import ExampleService, ExampleModel


class TestExampleService:
    """Test cases for ExampleService."""
    
    @pytest.fixture
    def service(self):
        """Create test service instance."""
        config = {"api_key": "test", "timeout": 30}
        return ExampleService(config)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample test data."""
        return ExampleModel(name="test", value=42)
    
    async def test_process_example_success(self, service, sample_data):
        """Test successful example processing."""
        # Given
        service._initialized = True
        
        # When
        result = await service.process_example(sample_data)
        
        # Then
        assert result["status"] == "success"
        assert result["processed_name"] == "TEST"
        assert result["processed_value"] == 84
    
    async def test_process_example_not_initialized(self, service, sample_data):
        """Test processing fails when service not initialized."""
        # Given
        service._initialized = False
        
        # When/Then
        with pytest.raises(RuntimeError, match="Service not initialized"):
            await service.process_example(sample_data)
    
    @patch('mcp_server.services.example.validate_input')
    async def test_process_example_validation_error(
        self, mock_validate, service, sample_data
    ):
        """Test processing fails on validation error."""
        # Given
        service._initialized = True
        mock_validate.side_effect = ValueError("Invalid input")
        
        # When/Then
        with pytest.raises(ValueError, match="Processing failed"):
            await service.process_example(sample_data)
```

#### Test Coverage
- Aim for **90%+ code coverage**
- Test both success and failure cases
- Include edge cases and boundary conditions
- Mock external dependencies
- Use descriptive test names

## 🏗️ Project Structure

When adding new features, follow this structure:

```
mcp_server/
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── server.py         # Main server logic
│   ├── auth.py           # Authentication
│   └── models.py         # Data models
├── services/             # Business logic services
│   ├── __init__.py
│   ├── devops.py         # DevOps analysis service
│   ├── sre.py            # SRE analysis service
│   └── cloud.py          # Cloud analysis service
├── plugins/              # Extensible plugins
│   ├── __init__.py
│   ├── base.py           # Base plugin class
│   └── kubernetes.py     # Kubernetes plugin
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── cache.py          # Caching utilities
│   └── validation.py     # Input validation
└── tests/                # Test files
    ├── unit/             # Unit tests
    ├── integration/      # Integration tests
    └── fixtures/         # Test fixtures
```

## 🔍 Code Review Process

### Pull Request Guidelines

1. **Title**: Use clear, descriptive titles
2. **Description**: Include:
   - What changes were made and why
   - How to test the changes
   - Any breaking changes
   - Screenshots/GIFs for UI changes
   - Links to related issues

3. **Size**: Keep PRs focused and reasonably sized
4. **Tests**: Include tests for new functionality
5. **Documentation**: Update relevant documentation

### Review Checklist

**For Authors:**
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Commit messages follow conventional commits
- [ ] No sensitive information is included
- [ ] Performance impact is considered

**For Reviewers:**
- [ ] Code is readable and maintainable
- [ ] Logic is correct and efficient
- [ ] Tests cover the changes adequately
- [ ] Security considerations are addressed
- [ ] Breaking changes are clearly documented

## 🏆 Recognition

Contributors will be recognized in several ways:

- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in changelog for significant contributions
- **GitHub**: Automatic contribution tracking
- **Community**: Recognition in Discord and community events

## 🆘 Getting Help

If you need help contributing:

1. **Documentation**: Check our [docs](https://docs.infragenius.ai)
2. **Discord**: Join our [community Discord](https://discord.gg/infragenius)
3. **GitHub Discussions**: Use [GitHub Discussions](https://github.com/infragenius/infragenius/discussions)
4. **Issues**: Create an issue with the `question` label

## 📞 Contact

- **Email**: contributors@infragenius.ai
- **Discord**: [Join our server](https://discord.gg/infragenius)
- **GitHub**: [@infragenius](https://github.com/infragenius)

---

## 🙏 Thank You

Thank you for contributing to InfraGenius! Your efforts help make DevOps and SRE practices more accessible to everyone.

**Happy coding!** 🚀
