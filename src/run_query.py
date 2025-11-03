#!/usr/bin/env python3
"""
Multi-Task Text Utility - Main Application
Processes user questions using OpenAI API with prompt engineering techniques
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI
from pathlib import Path

# Import safety module
from src.safety import SafetyChecker


class TextUtility:
    """
    Multi-task text utility that processes user queries using OpenAI API.
    Implements few-shot learning and chain-of-thought prompting techniques.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the text utility with OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.safety_checker = SafetyChecker(self.client)
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
        
        # Pricing per 1K tokens (as of 2024, adjust as needed)
        self.pricing = {
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        }
    
    def _load_prompt_template(self) -> str:
        """Load the prompt template from file."""
        template_path = Path(__file__).parent.parent / "prompts" / "main_prompt.txt"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt template not found at {template_path}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Fallback prompt template."""
        return """You are a helpful AI assistant that processes user questions and provides structured responses.

Analyze the user's question and provide a comprehensive answer in the following JSON format:
{
    "question_type": "type of question (e.g., factual, analytical, creative, technical)",
    "answer": "detailed answer to the question",
    "confidence": "high/medium/low",
    "additional_context": "any relevant additional information"
}

User question: {question}"""
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of the API call."""
        model_key = self.model
        if model_key not in self.pricing:
            # Default to gpt-3.5-turbo pricing for unknown models
            model_key = "gpt-3.5-turbo"
        
        pricing = self.pricing[model_key]
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        return prompt_cost + completion_cost
    
    def process_query(self, user_question: str, check_safety: bool = True) -> Dict[str, Any]:
        """
        Process a user query and return structured JSON response.
        
        Args:
            user_question: The user's question
            check_safety: Whether to check for adversarial prompts
            
        Returns:
            Dictionary containing response and metrics
        """
        start_time = time.time()
        
        # Safety check
        if check_safety:
            safety_result = self.safety_checker.check_prompt(user_question)
            if not safety_result["is_safe"]:
                return {
                    "status": "rejected",
                    "reason": "Safety check failed",
                    "safety_analysis": safety_result,
                    "timestamp": datetime.now().isoformat(),
                    "metrics": {
                        "tokens_prompt": 0,
                        "tokens_completion": 0,
                        "total_tokens": 0,
                        "latency_ms": int((time.time() - start_time) * 1000),
                        "estimated_cost": 0.0
                    }
                }
        
        # Prepare the prompt with few-shot examples
        prompt = self.prompt_template.replace("{question}", user_question)
        
        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that provides structured, accurate responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Calculate metrics
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            estimated_cost = self._calculate_cost(prompt_tokens, completion_tokens)
            
            # Parse response
            response_content = response.choices[0].message.content
            parsed_response = json.loads(response_content)
            
            # Construct result
            result = {
                "status": "success",
                "response": parsed_response,
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "metrics": {
                    "tokens_prompt": prompt_tokens,
                    "tokens_completion": completion_tokens,
                    "total_tokens": total_tokens,
                    "latency_ms": latency_ms,
                    "estimated_cost": round(estimated_cost, 6)
                }
            }
            
            # Log metrics
            self._log_metrics(result["metrics"], user_question)
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error": f"Failed to parse JSON response: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _log_metrics(self, metrics: Dict[str, Any], question: str):
        """Log metrics to CSV file."""
        metrics_dir = Path(__file__).parent.parent / "metrics"
        metrics_dir.mkdir(exist_ok=True)
        
        csv_path = metrics_dir / "metrics.csv"
        json_path = metrics_dir / "metrics.json"
        
        # Prepare metrics entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tokens_prompt": metrics["tokens_prompt"],
            "tokens_completion": metrics["tokens_completion"],
            "total_tokens": metrics["total_tokens"],
            "latency_ms": metrics["latency_ms"],
            "estimated_cost": metrics["estimated_cost"],
            "model": self.model,
            "question_preview": question[:50] + "..." if len(question) > 50 else question
        }
        
        # Log to CSV
        import csv
        file_exists = csv_path.exists()
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(entry)
        
        # Log to JSON (append to array)
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        data.append(entry)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


def main():
    """Main entry point for the application."""
    import sys
    
    # Check for command line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m src.run_query <question>")
        print("       or set question via stdin")
        print("\nExample: python -m src.run_query 'What is machine learning?'")
        sys.exit(1)
    
    # Get question from command line
    question = " ".join(sys.argv[1:])
    
    # Initialize utility
    utility = TextUtility()
    
    # Process query
    print(f"Processing question: {question}\n")
    result = utility.process_query(question)
    
    # Print result as formatted JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
