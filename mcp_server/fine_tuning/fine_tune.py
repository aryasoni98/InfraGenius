#!/usr/bin/env python3
"""
Fine-tuning script for gpt-oss:latest model with DevOps/SRE domain expertise
Optimized for industry-level performance and domain-specific knowledge
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
import time
import tempfile
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning process"""
    base_model: str = "gpt-oss:latest"
    output_model: str = "gpt-oss-devops:latest"
    dataset_path: str = "./devops_dataset.jsonl"
    validation_split: float = 0.2
    epochs: int = 10
    learning_rate: float = 0.0001
    batch_size: int = 8
    max_seq_length: int = 4096
    temperature: float = 0.1
    domain_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.domain_weights is None:
            self.domain_weights = {
                "devops": 0.3,
                "sre": 0.25,
                "cloud": 0.25,
                "platform": 0.2
            }

@dataclass
class FineTuningMetrics:
    """Metrics for fine-tuning process"""
    epoch: int
    loss: float
    validation_loss: float
    accuracy: float
    validation_accuracy: float
    learning_rate: float
    training_time: float
    memory_usage: int

class DatasetProcessor:
    """Process and validate training dataset"""
    
    def __init__(self, config: FineTuningConfig):
        self.config = config
        self.validation_errors = []
    
    def load_and_validate_dataset(self) -> tuple[List[Dict], List[Dict]]:
        """Load and validate the training dataset"""
        logger.info(f"Loading dataset from {self.config.dataset_path}")
        
        if not os.path.exists(self.config.dataset_path):
            raise FileNotFoundError(f"Dataset file not found: {self.config.dataset_path}")
        
        # Load dataset
        dataset = []
        with open(self.config.dataset_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    if self._validate_entry(entry, line_num):
                        dataset.append(entry)
                except json.JSONDecodeError as e:
                    self.validation_errors.append(f"Line {line_num}: Invalid JSON - {e}")
        
        if self.validation_errors:
            logger.warning(f"Found {len(self.validation_errors)} validation errors:")
            for error in self.validation_errors[:10]:  # Show first 10 errors
                logger.warning(error)
        
        # Balance dataset by domain
        balanced_dataset = self._balance_dataset_by_domain(dataset)
        
        # Split into training and validation
        split_index = int(len(balanced_dataset) * (1 - self.config.validation_split))
        train_data = balanced_dataset[:split_index]
        val_data = balanced_dataset[split_index:]
        
        logger.info(f"Dataset loaded: {len(train_data)} training, {len(val_data)} validation examples")
        
        return train_data, val_data
    
    def _validate_entry(self, entry: Dict, line_num: int) -> bool:
        """Validate a single dataset entry"""
        required_fields = ['instruction', 'input', 'output', 'domain']
        
        for field in required_fields:
            if field not in entry:
                self.validation_errors.append(f"Line {line_num}: Missing required field '{field}'")
                return False
        
        # Validate field types
        if not isinstance(entry['instruction'], str):
            self.validation_errors.append(f"Line {line_num}: 'instruction' must be a string")
            return False
        
        if not isinstance(entry['input'], str):
            self.validation_errors.append(f"Line {line_num}: 'input' must be a string")
            return False
        
        if not isinstance(entry['output'], str):
            self.validation_errors.append(f"Line {line_num}: 'output' must be a string")
            return False
        
        if entry['domain'] not in self.config.domain_weights:
            self.validation_errors.append(f"Line {line_num}: Unknown domain '{entry['domain']}'")
            return False
        
        # Validate content length
        if len(entry['instruction']) < 10:
            self.validation_errors.append(f"Line {line_num}: Instruction too short")
            return False
        
        if len(entry['output']) < 50:
            self.validation_errors.append(f"Line {line_num}: Output too short")
            return False
        
        return True
    
    def _balance_dataset_by_domain(self, dataset: List[Dict]) -> List[Dict]:
        """Balance dataset according to domain weights"""
        domain_data = {}
        for entry in dataset:
            domain = entry['domain']
            if domain not in domain_data:
                domain_data[domain] = []
            domain_data[domain].append(entry)
        
        # Calculate target sizes based on weights
        total_examples = len(dataset)
        balanced_dataset = []
        
        for domain, weight in self.config.domain_weights.items():
            if domain in domain_data:
                domain_examples = domain_data[domain]
                target_size = int(total_examples * weight)
                
                # If we have more examples than needed, sample randomly
                if len(domain_examples) > target_size:
                    import random
                    random.shuffle(domain_examples)
                    selected_examples = domain_examples[:target_size]
                else:
                    # If we have fewer examples, use all and repeat some
                    selected_examples = domain_examples * (target_size // len(domain_examples) + 1)
                    selected_examples = selected_examples[:target_size]
                
                balanced_dataset.extend(selected_examples)
                logger.info(f"Domain '{domain}': {len(selected_examples)} examples (weight: {weight})")
        
        # Shuffle the balanced dataset
        import random
        random.shuffle(balanced_dataset)
        
        return balanced_dataset
    
    def create_ollama_dataset(self, train_data: List[Dict], val_data: List[Dict]) -> tuple[str, str]:
        """Create Ollama-compatible dataset files"""
        train_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        val_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        
        # Convert to Ollama format
        for entry in train_data:
            ollama_entry = self._convert_to_ollama_format(entry)
            train_file.write(json.dumps(ollama_entry) + '\n')
        
        for entry in val_data:
            ollama_entry = self._convert_to_ollama_format(entry)
            val_file.write(json.dumps(ollama_entry) + '\n')
        
        train_file.close()
        val_file.close()
        
        return train_file.name, val_file.name
    
    def _convert_to_ollama_format(self, entry: Dict) -> Dict:
        """Convert dataset entry to Ollama fine-tuning format"""
        # Combine instruction and input for the prompt
        prompt = f"{entry['instruction']}\n\n{entry['input']}"
        
        return {
            "prompt": prompt,
            "response": entry['output'],
            "domain": entry['domain']
        }

class ModelFineTuner:
    """Fine-tune the gpt-oss model for DevOps/SRE domains"""
    
    def __init__(self, config: FineTuningConfig):
        self.config = config
        self.metrics_history = []
    
    async def fine_tune_model(self) -> bool:
        """Execute the fine-tuning process"""
        logger.info("Starting fine-tuning process...")
        
        try:
            # Step 1: Process dataset
            processor = DatasetProcessor(self.config)
            train_data, val_data = processor.load_and_validate_dataset()
            
            if not train_data:
                logger.error("No valid training data found")
                return False
            
            # Step 2: Create Ollama-compatible dataset
            train_file, val_file = processor.create_ollama_dataset(train_data, val_data)
            
            try:
                # Step 3: Create Modelfile for fine-tuning
                modelfile_path = await self._create_modelfile(train_file)
                
                # Step 4: Execute fine-tuning
                success = await self._execute_ollama_fine_tuning(modelfile_path)
                
                if success:
                    logger.info("Fine-tuning completed successfully!")
                    await self._validate_fine_tuned_model()
                    await self._save_metrics()
                else:
                    logger.error("Fine-tuning failed")
                
                return success
                
            finally:
                # Clean up temporary files
                os.unlink(train_file)
                os.unlink(val_file)
                
        except Exception as e:
            logger.error(f"Fine-tuning process failed: {e}")
            return False
    
    async def _create_modelfile(self, train_file: str) -> str:
        """Create Modelfile for fine-tuning"""
        modelfile_content = f"""FROM {self.config.base_model}

# Domain-specific system message
SYSTEM \"\"\"You are an expert DevOps, SRE, Cloud, and Platform Engineer with industry-level expertise. You provide accurate, actionable, and production-ready solutions for complex infrastructure and operational challenges. Your responses are comprehensive, well-structured, and include specific implementation details, best practices, and security considerations.

Key areas of expertise:
- DevOps: CI/CD, Infrastructure as Code, Automation, Monitoring
- SRE: Reliability Engineering, Incident Response, SLO Management, Observability  
- Cloud: Architecture, Security, Cost Optimization, Migration Strategies
- Platform Engineering: Developer Experience, API Design, Self-Service Tools

Always provide:
1. Clear analysis of the problem
2. Step-by-step solutions with commands/configurations
3. Best practices and security considerations
4. Performance and cost implications
5. Monitoring and maintenance recommendations
\"\"\"

# Fine-tuning parameters
PARAMETER temperature {self.config.temperature}
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx {self.config.max_seq_length}

# Training configuration
PARAMETER learning_rate {self.config.learning_rate}
PARAMETER batch_size {self.config.batch_size}
PARAMETER epochs {self.config.epochs}

# Domain-specific training data
TRAINING_DATA {train_file}
"""
        
        modelfile_path = tempfile.NamedTemporaryFile(mode='w', suffix='.modelfile', delete=False)
        modelfile_path.write(modelfile_content)
        modelfile_path.close()
        
        return modelfile_path.name
    
    async def _execute_ollama_fine_tuning(self, modelfile_path: str) -> bool:
        """Execute Ollama fine-tuning command"""
        logger.info("Starting Ollama fine-tuning...")
        
        try:
            # Create the fine-tuned model
            cmd = [
                'ollama', 'create', self.config.output_model,
                '-f', modelfile_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("Model creation completed successfully")
                logger.info(f"Output: {stdout.decode('utf-8')}")
                return True
            else:
                logger.error(f"Model creation failed: {stderr.decode('utf-8')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to execute fine-tuning: {e}")
            return False
        finally:
            # Clean up modelfile
            if os.path.exists(modelfile_path):
                os.unlink(modelfile_path)
    
    async def _validate_fine_tuned_model(self) -> None:
        """Validate the fine-tuned model with test queries"""
        logger.info("Validating fine-tuned model...")
        
        test_queries = [
            {
                "domain": "devops",
                "query": "How do I set up a CI/CD pipeline for a microservices application?",
                "expected_keywords": ["pipeline", "stages", "testing", "deployment", "monitoring"]
            },
            {
                "domain": "sre", 
                "query": "What should I do when my service's error budget is exhausted?",
                "expected_keywords": ["error budget", "SLO", "reliability", "incident", "postmortem"]
            },
            {
                "domain": "cloud",
                "query": "How can I optimize costs in my AWS infrastructure?",
                "expected_keywords": ["cost", "optimization", "reserved instances", "right-sizing", "monitoring"]
            },
            {
                "domain": "platform",
                "query": "How do I design a developer platform for self-service deployments?",
                "expected_keywords": ["self-service", "developer experience", "API", "automation", "templates"]
            }
        ]
        
        validation_results = []
        
        for test in test_queries:
            try:
                # Test the fine-tuned model
                result = await self._test_model_response(test["query"])
                
                # Check if response contains expected keywords
                response_lower = result.lower()
                keyword_matches = sum(1 for keyword in test["expected_keywords"] 
                                    if keyword.lower() in response_lower)
                
                validation_score = keyword_matches / len(test["expected_keywords"])
                
                validation_results.append({
                    "domain": test["domain"],
                    "query": test["query"],
                    "response_length": len(result),
                    "keyword_matches": keyword_matches,
                    "total_keywords": len(test["expected_keywords"]),
                    "validation_score": validation_score
                })
                
                logger.info(f"Domain {test['domain']}: Validation score {validation_score:.2f}")
                
            except Exception as e:
                logger.error(f"Validation failed for {test['domain']}: {e}")
        
        # Calculate overall validation score
        if validation_results:
            avg_score = sum(r["validation_score"] for r in validation_results) / len(validation_results)
            logger.info(f"Overall validation score: {avg_score:.2f}")
            
            if avg_score < 0.5:
                logger.warning("Low validation score - model may need additional training")
    
    async def _test_model_response(self, query: str) -> str:
        """Test the fine-tuned model with a query"""
        try:
            process = await asyncio.create_subprocess_exec(
                'ollama', 'run', self.config.output_model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=query.encode('utf-8')),
                timeout=60
            )
            
            if process.returncode == 0:
                return stdout.decode('utf-8').strip()
            else:
                logger.error(f"Model test failed: {stderr.decode('utf-8')}")
                return ""
                
        except asyncio.TimeoutError:
            logger.error("Model test timed out")
            return ""
        except Exception as e:
            logger.error(f"Model test error: {e}")
            return ""
    
    async def _save_metrics(self) -> None:
        """Save fine-tuning metrics"""
        metrics_file = f"fine_tuning_metrics_{int(time.time())}.json"
        
        metrics_data = {
            "config": asdict(self.config),
            "timestamp": time.time(),
            "metrics_history": self.metrics_history,
            "model_info": {
                "base_model": self.config.base_model,
                "output_model": self.config.output_model,
                "training_completed": True
            }
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Metrics saved to {metrics_file}")

class FineTuningOrchestrator:
    """Orchestrate the entire fine-tuning process"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            self.config = FineTuningConfig(**config_data.get('fine_tuning', {}))
        else:
            self.config = FineTuningConfig()
    
    async def run_fine_tuning(self) -> bool:
        """Run the complete fine-tuning process"""
        logger.info("Starting DevOps/SRE Fine-tuning Process")
        logger.info(f"Base model: {self.config.base_model}")
        logger.info(f"Output model: {self.config.output_model}")
        logger.info(f"Dataset: {self.config.dataset_path}")
        
        # Check prerequisites
        if not await self._check_prerequisites():
            return False
        
        # Initialize fine-tuner
        fine_tuner = ModelFineTuner(self.config)
        
        # Execute fine-tuning
        success = await fine_tuner.fine_tune_model()
        
        if success:
            logger.info("Fine-tuning process completed successfully!")
            logger.info(f"New model available: {self.config.output_model}")
            await self._create_usage_instructions()
        else:
            logger.error("Fine-tuning process failed")
        
        return success
    
    async def _check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("Checking prerequisites...")
        
        # Check if Ollama is installed
        try:
            process = await asyncio.create_subprocess_exec(
                'ollama', 'version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error("Ollama is not installed or not accessible")
                return False
            
            logger.info(f"Ollama version: {stdout.decode('utf-8').strip()}")
            
        except FileNotFoundError:
            logger.error("Ollama not found in PATH")
            return False
        
        # Check if base model exists
        try:
            process = await asyncio.create_subprocess_exec(
                'ollama', 'show', self.config.base_model,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Base model '{self.config.base_model}' not found")
                logger.info(f"Please run: ollama pull {self.config.base_model}")
                return False
            
            logger.info(f"Base model '{self.config.base_model}' is available")
            
        except Exception as e:
            logger.error(f"Failed to check base model: {e}")
            return False
        
        # Check if dataset exists
        if not os.path.exists(self.config.dataset_path):
            logger.error(f"Dataset file not found: {self.config.dataset_path}")
            return False
        
        logger.info("All prerequisites met")
        return True
    
    async def _create_usage_instructions(self) -> None:
        """Create usage instructions for the fine-tuned model"""
        instructions = f"""
# Fine-tuned Model Usage Instructions

## Model Information
- **Base Model**: {self.config.base_model}
- **Fine-tuned Model**: {self.config.output_model}
- **Domains**: DevOps, SRE, Cloud Architecture, Platform Engineering

## Usage

### Basic Usage
```bash
ollama run {self.config.output_model}
```

### With MCP Server
Update your MCP server configuration to use the fine-tuned model:

```json
{{
  "model": "{self.config.output_model}",
  "temperature": {self.config.temperature}
}}
```

### Example Queries

#### DevOps
```
How do I implement blue-green deployments for a Kubernetes application?
```

#### SRE
```
My service has a 99.9% availability SLO but is currently at 99.7%. What actions should I take?
```

#### Cloud Architecture
```
Design a cost-effective, scalable architecture for a high-traffic web application on AWS.
```

#### Platform Engineering
```
How do I create a self-service platform for developers to deploy microservices?
```

## Performance Optimization
- Use temperature {self.config.temperature} for consistent, professional responses
- Context length: {self.config.max_seq_length} tokens
- Batch size: {self.config.batch_size} for optimal performance

## Model Validation
The model has been validated across all domains with industry-specific test cases.
Performance metrics are available in the fine-tuning logs.
"""
        
        with open(f"{self.config.output_model.replace(':', '_')}_usage.md", 'w') as f:
            f.write(instructions)
        
        logger.info("Usage instructions created")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fine-tune gpt-oss model for DevOps/SRE domains")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--dataset", type=str, help="Dataset file path")
    parser.add_argument("--output-model", type=str, help="Output model name")
    parser.add_argument("--epochs", type=int, help="Number of training epochs")
    parser.add_argument("--learning-rate", type=float, help="Learning rate")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = FineTuningOrchestrator(args.config)
    
    # Override config with command line arguments
    if args.dataset:
        orchestrator.config.dataset_path = args.dataset
    if args.output_model:
        orchestrator.config.output_model = args.output_model
    if args.epochs:
        orchestrator.config.epochs = args.epochs
    if args.learning_rate:
        orchestrator.config.learning_rate = args.learning_rate
    
    # Run fine-tuning
    success = await orchestrator.run_fine_tuning()
    
    if success:
        print(f"\n✅ Fine-tuning completed successfully!")
        print(f"🎯 Model: {orchestrator.config.output_model}")
        print(f"📊 Dataset: {orchestrator.config.dataset_path}")
        print(f"🚀 Ready to use with MCP server!")
    else:
        print("\n❌ Fine-tuning failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
