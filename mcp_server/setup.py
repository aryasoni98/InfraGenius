#!/usr/bin/env python3
"""
Setup script for DevOps/SRE/Cloud/Platform Engineering MCP Server
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="devops-sre-mcp-server",
    version="1.0.0",
    author="DevOps SRE Team",
    author_email="devops@logify360.com",
    description="Advanced MCP Server for DevOps, SRE, Cloud, and Platform Engineering with industry-level expertise",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/logify360/devops-sre-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "pre-commit>=3.6.0",
        ],
        "ml": [
            "torch>=2.1.0",
            "transformers>=4.35.0",
            "datasets>=2.15.0",
            "accelerate>=0.25.0",
            "sentence-transformers>=2.2.2",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "grafana-api>=1.0.3",
            "elasticsearch>=8.11.0",
            "jaeger-client>=4.8.0",
        ],
        "cloud": [
            "boto3>=1.34.0",
            "azure-identity>=1.15.0",
            "azure-mgmt-resource>=23.0.0",
            "google-cloud-core>=2.4.0",
            "google-auth>=2.23.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "devops-mcp-server=server:main",
            "devops-fine-tune=fine_tuning.fine_tune:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.md", "*.txt"],
    },
    zip_safe=False,
)
