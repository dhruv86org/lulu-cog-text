#!/usr/bin/env python3
"""
Project Validation Script
Verifies that all required deliverables are present and correctly structured
"""

import os
import json
from pathlib import Path


class ProjectValidator:
    """Validates project structure and deliverables."""
    
    def __init__(self):
        self.root = Path(__file__).parent
        self.passed = []
        self.failed = []
    
    def check_file_exists(self, filepath, description):
        """Check if a file exists."""
        full_path = self.root / filepath
        if full_path.exists():
            self.passed.append(f"? {description}: {filepath}")
            return True
        else:
            self.failed.append(f"? {description}: {filepath} NOT FOUND")
            return False
    
    def check_directory_exists(self, dirpath, description):
        """Check if a directory exists."""
        full_path = self.root / dirpath
        if full_path.exists() and full_path.is_dir():
            self.passed.append(f"? {description}: {dirpath}/")
            return True
        else:
            self.failed.append(f"? {description}: {dirpath}/ NOT FOUND")
            return False
    
    def check_file_content(self, filepath, required_strings, description):
        """Check if file contains required content."""
        full_path = self.root / filepath
        if not full_path.exists():
            self.failed.append(f"? {description}: File not found")
            return False
        
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        missing = [s for s in required_strings if s not in content]
        if not missing:
            self.passed.append(f"? {description}: Contains required content")
            return True
        else:
            self.failed.append(f"? {description}: Missing content: {missing}")
            return False
    
    def validate_all(self):
        """Run all validation checks."""
        print("="*70)
        print("  PROJECT VALIDATION")
        print("="*70)
        print()
        
        # Check main application
        print("?? CORE APPLICATION FILES")
        self.check_file_exists("src/run_query.py", "Main application script")
        self.check_file_content(
            "src/run_query.py",
            ["TextUtility", "OpenAI", "process_query", "metrics"],
            "Main app has required classes/functions"
        )
        
        # Check safety module
        self.check_file_exists("src/safety.py", "Safety module")
        self.check_file_content(
            "src/safety.py",
            ["SafetyChecker", "check_prompt", "adversarial"],
            "Safety module has required functionality"
        )
        
        # Check package init
        self.check_file_exists("src/__init__.py", "Package initializer")
        
        print()
        print("?? PROMPT TEMPLATE")
        self.check_file_exists("prompts/main_prompt.txt", "Prompt template")
        self.check_file_content(
            "prompts/main_prompt.txt",
            ["INSTRUCTIONS", "Example", "{question}", "JSON"],
            "Prompt has instructions and examples"
        )
        
        print()
        print("?? METRICS & LOGGING")
        self.check_directory_exists("metrics", "Metrics directory")
        
        print()
        print("?? DOCUMENTATION")
        self.check_file_exists("README.md", "README")
        self.check_file_content(
            "README.md",
            ["Setup", "Installation", "Usage", "Metrics"],
            "README has required sections"
        )
        
        self.check_file_exists("reports/PI_report_en.md", "Technical report")
        self.check_file_content(
            "reports/PI_report_en.md",
            ["Architecture", "Prompt", "Metrics", "Safety"],
            "Report has required sections"
        )
        
        print()
        print("?? TESTING")
        self.check_file_exists("tests/test_core.py", "Test suite")
        self.check_file_content(
            "tests/test_core.py",
            ["test_", "assert", "pytest", "TestJSONValidation", "TestTokenCounting"],
            "Tests have proper structure"
        )
        
        print()
        print("??  CONFIGURATION")
        self.check_file_exists("requirements.txt", "Dependencies file")
        self.check_file_content(
            "requirements.txt",
            ["openai", "pytest"],
            "Required dependencies listed"
        )
        
        print()
        print("?? BONUS FILES")
        self.check_file_exists("demo.py", "Demo script")
        self.check_file_exists("QUICKSTART.md", "Quick start guide")
        self.check_file_exists("PROJECT_SUMMARY.md", "Project summary")
        
        print()
        print("="*70)
        print("  VALIDATION RESULTS")
        print("="*70)
        print()
        
        for item in self.passed:
            print(item)
        
        if self.failed:
            print()
            print("FAILURES:")
            for item in self.failed:
                print(item)
        
        print()
        print("-"*70)
        print(f"? Passed: {len(self.passed)}")
        print(f"? Failed: {len(self.failed)}")
        print("-"*70)
        
        if not self.failed:
            print()
            print("?? SUCCESS! All required deliverables are present and valid.")
            print()
            print("Next steps:")
            print("  1. Set OPENAI_API_KEY environment variable")
            print("  2. Install dependencies: pip install -r requirements.txt")
            print("  3. Run demo: python demo.py")
            print("  4. Run tests: pytest tests/test_core.py -v")
            print()
            return True
        else:
            print()
            print("??  Some required files or content are missing.")
            print("   Please review the failures above.")
            print()
            return False


def main():
    """Main validation entry point."""
    validator = ProjectValidator()
    success = validator.validate_all()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
