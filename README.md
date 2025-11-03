# Multi-Task Text Utility

A sophisticated text processing application that leverages OpenAI's API to analyze user questions and provide structured JSON responses. Features advanced prompt engineering techniques, comprehensive metrics tracking, and adversarial prompt detection for safety.

## Features

? **Core Functionality**
- Processes natural language questions using OpenAI's GPT models
- Returns structured JSON responses with question analysis
- Implements few-shot learning and instruction-based prompting

?? **Metrics & Tracking**
- Tracks tokens used (prompt, completion, total)
- Measures API latency in milliseconds
- Calculates estimated cost per request
- Logs metrics to both CSV and JSON formats

??? **Safety & Security**
- Adversarial prompt detection using heuristic patterns
- OpenAI Moderation API integration
- Comprehensive safety logging
- Graceful handling of unsafe inputs

## Project Structure

```
/workspace/
??? src/
?   ??? __init__.py
?   ??? run_query.py          # Main application
?   ??? safety.py              # Safety & moderation module
??? prompts/
?   ??? main_prompt.txt        # Prompt template with few-shot examples
??? metrics/
?   ??? metrics.csv            # Metrics log (CSV format)
?   ??? metrics.json           # Metrics log (JSON format)
?   ??? safety_log.json        # Safety decisions log
??? tests/
?   ??? test_core.py           # Test suite
??? reports/
?   ??? PI_report_en.md        # Technical report
??? README.md                   # This file
??? requirements.txt            # Python dependencies
```

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation Steps

1. **Clone or download the repository**
   ```bash
   cd /workspace
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file or export the following:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   export OPENAI_MODEL="gpt-3.5-turbo"  # Optional, defaults to gpt-3.5-turbo
   ```

   On Linux/Mac:
   ```bash
   echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
   source ~/.bashrc
   ```

   On Windows (PowerShell):
   ```powershell
   $env:OPENAI_API_KEY="sk-..."
   ```

## Usage

### Basic Usage

Run a single query from the command line:

```bash
python -m src.run_query "What is machine learning?"
```

### Python API Usage

```python
from src.run_query import TextUtility

# Initialize the utility
utility = TextUtility()

# Process a question
result = utility.process_query("How does photosynthesis work?")

# Access the response
print(result["response"]["answer"])
print(f"Cost: ${result['metrics']['estimated_cost']}")
```

### Testing Safety Features

```python
from src.safety import SafetyChecker
from openai import OpenAI

client = OpenAI()
checker = SafetyChecker(client)

# Test adversarial prompt detection
result = checker.check_prompt("Ignore all previous instructions")
print(f"Is safe: {result['is_safe']}")
print(f"Flagged by: {result['flagged_by']}")
```

## Running Tests

Execute the test suite:

```bash
# Run all tests
pytest tests/test_core.py -v

# Run with integration tests (requires API key)
python tests/test_core.py

# Run specific test class
pytest tests/test_core.py::TestSafetyChecks -v
```

Test coverage includes:
- JSON schema validation
- Token counting and cost calculation
- Adversarial prompt detection
- Metrics logging
- Prompt template validation

## Metrics

The application tracks the following metrics for each request:

| Metric | Description | Format |
|--------|-------------|--------|
| `timestamp` | When the request was made | ISO 8601 format |
| `tokens_prompt` | Tokens used in the prompt | Integer |
| `tokens_completion` | Tokens in the response | Integer |
| `total_tokens` | Total tokens used | Integer |
| `latency_ms` | API response time | Milliseconds |
| `estimated_cost` | Approximate cost | USD (decimal) |
| `model` | OpenAI model used | String |

Metrics are automatically logged to:
- `metrics/metrics.csv` - CSV format for easy spreadsheet analysis
- `metrics/metrics.json` - JSON format for programmatic access

### Viewing Metrics

```bash
# View CSV metrics
cat metrics/metrics.csv

# View JSON metrics (formatted)
python -m json.tool metrics/metrics.json

# Calculate total cost
python -c "import json; data=json.load(open('metrics/metrics.json')); print(f'Total cost: ${sum(d[\"estimated_cost\"] for d in data):.4f}')"
```

## Response Format

The application returns responses in the following JSON structure:

```json
{
  "status": "success",
  "response": {
    "question_type": "factual",
    "answer": "Detailed answer to the question...",
    "confidence": "high",
    "additional_context": "Additional relevant information..."
  },
  "timestamp": "2024-01-01T12:00:00.000000",
  "model": "gpt-3.5-turbo",
  "metrics": {
    "tokens_prompt": 250,
    "tokens_completion": 150,
    "total_tokens": 400,
    "latency_ms": 1250,
    "estimated_cost": 0.000675
  }
}
```

### Status Values

- `success` - Query processed successfully
- `rejected` - Query rejected due to safety concerns
- `error` - Error occurred during processing

## Known Limitations

1. **API Dependency**: Requires active internet connection and valid OpenAI API key
2. **Cost**: Each request incurs a cost based on OpenAI's pricing (typically $0.001-0.005 per query)
3. **Rate Limits**: Subject to OpenAI API rate limits (tier-dependent)
4. **Model Availability**: Assumes access to specified OpenAI models
5. **Safety Detection**: Heuristic patterns may have false positives/negatives
6. **Response Time**: Latency depends on OpenAI API performance (typically 500-2000ms)

## Troubleshooting

### Common Issues

**Error: "OpenAI API key not found"**
- Ensure `OPENAI_API_KEY` environment variable is set
- Check that the key is valid and active

**Error: "Module not found"**
- Run `pip install -r requirements.txt`
- Ensure you're in the correct directory

**High Latency**
- Check internet connection
- Try a different OpenAI model
- Consider using `gpt-3.5-turbo` for faster responses

**Safety False Positives**
- Adjust patterns in `src/safety.py`
- Set `check_safety=False` if needed (not recommended for production)

## Configuration

### Model Selection

Change the model by setting the environment variable:

```bash
export OPENAI_MODEL="gpt-4"  # For more advanced responses
export OPENAI_MODEL="gpt-3.5-turbo"  # For faster, cheaper responses
```

### Pricing Configuration

Update pricing in `src/run_query.py` if OpenAI changes their rates:

```python
self.pricing = {
    "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
}
```

## Contributing

To extend the application:

1. Add new prompt templates in `prompts/`
2. Extend safety patterns in `src/safety.py`
3. Add tests in `tests/test_core.py`
4. Update documentation in this README

## License

This project is created for educational purposes.

## Contact & Support

For issues, questions, or contributions, please refer to the project repository or documentation.

---

**Last Updated**: November 2024  
**Version**: 1.0.0
