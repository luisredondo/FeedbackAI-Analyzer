# RAG Evaluation Framework

A simple, file-based evaluation system for comparing different retrieval strategies in the Client Feedback Analyzer.

## Features

- **Golden Dataset Generation**: Creates synthetic question-answer pairs from feedback data
- **Multiple Retrieval Strategies**: Supports naive (vector similarity), BM25, multi-query, parent-document, rerank, and ensemble retrievers
- **Comprehensive Metrics**: Evaluates faithfulness, answer relevancy, context precision, context recall, latency, and cost
- **LangSmith Integration**: Uploads datasets and tracks experiments
- **Markdown Results**: Beautiful, readable results saved to `results/` folder
- **Simple Execution**: Just run Python files directly

## Quick Start

### 1. Set up your environment with `uv`

First, ensure you have `uv` installed and set up your project:

```bash
# Install dependencies using uv (this will create .venv automatically)
uv sync

# Alternatively, if you prefer to use the existing requirements.txt:
uv venv
uv pip install -r requirements.txt

# Activate the virtual environment (optional - uv run handles this automatically)
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

Ensure your `.env` file contains:
```
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key  # For rerank retriever
LANGCHAIN_API_KEY=your_langsmith_api_key
```

### 2. Run evaluations

Choose one of the evaluation scripts based on your needs:

#### Quick Console Evaluation
```bash
# Fast evaluation with console output only
uv run python evaluation/quick_eval.py
```

#### Naive vs Advanced Comparison 
```bash
# Compare naive vs advanced retriever (saves markdown results)
uv run python evaluation/run_naive_vs_advanced.py
```

#### Complete Evaluation
```bash
# Evaluate all retrievers (comprehensive markdown report)
uv run python evaluation/run_all_retrievers.py
```

### 3. View results

Results are automatically saved to the `results/` folder:
- `results/evaluation_results.md` - Naive vs Advanced comparison
- `results/all_retrievers_results.md` - Complete evaluation report

## Available Retrievers

- **naive**: Simple vector similarity search
- **bm25**: Keyword-based search (BM25 algorithm)
- **multi_query**: Generates multiple search queries for better recall
- **parent_document**: Hierarchical chunking with parent-child relationships
- **rerank**: Uses Cohere to rerank retrieved documents
- **ensemble**: Combines BM25 and vector search

## Evaluation Metrics

- **Context Recall**: How well the retriever finds relevant contexts
- **Faithfulness**: How accurately the answer reflects the retrieved context
- **Answer Relevancy**: How relevant the answer is to the question
- **Context Precision**: How precise the retrieved contexts are
- **Average Latency**: Response time in seconds
- **Total Cost**: OpenAI API costs in USD

## Programmatic Usage

```python
# First activate the uv environment:
# source .venv/bin/activate  (macOS/Linux)
# .venv\Scripts\activate     (Windows)

from evaluation.evaluator import RAGEvaluator

# Initialize evaluator
evaluator = RAGEvaluator("backend/data/feedback_corpus.csv")

# Generate golden dataset
evaluator.generate_golden_dataset(test_size=15)

# Compare specific retrievers
results = evaluator.compare_retrievers(["naive", "parent_document"])

# Evaluate all retrievers
all_results = evaluator.evaluate_all_retrievers(test_size=15)
```

## Available Evaluation Scripts

### 1. `quick_eval.py`
- **Purpose**: Fast evaluation with console output
- **Output**: Results printed to terminal only
- **Use case**: Quick testing and debugging

### 2. `run_naive_vs_advanced.py`  
- **Purpose**: Compare naive vs one advanced retriever
- **Output**: `results/evaluation_results.md`
- **Use case**: Focused comparison for decision making

### 3. `run_all_retrievers.py`
- **Purpose**: Comprehensive evaluation of all retrievers
- **Output**: `results/all_retrievers_results.md` 
- **Use case**: Complete analysis with recommendations

### Note for `uv` Users

The `uv run` command automatically:
- Creates and manages the virtual environment
- Installs dependencies from `pyproject.toml`
- Runs the script with the correct Python path

Simply run: `uv run python evaluation/<script_name>.py`

## Output Format

The evaluation produces beautiful markdown reports in the `results/` folder with:

### Evaluation Results Table
| Retriever | Context Recall | Faithfulness | Answer Relevancy | Context Precision | Avg Latency (s) | Total Cost ($) |
|-----------|----------------|--------------|------------------|-------------------|-----------------|----------------|
| parent_document | 0.8542 | 0.9234 | 0.8876 | 0.7654 | 2.34 | 0.0456 |
| naive | 0.7234 | 0.8567 | 0.8234 | 0.6987 | 1.87 | 0.0234 |

### Analysis & Recommendations
- **Best performer identification**
- **Speed vs quality trade-offs**
- **Cost-effectiveness analysis**
- **Detailed methodology**
- **Configuration details**
- **Actionable recommendations**

## Benefits

1. **Clear Decision Making**: Markdown tables make it easy to compare retrievers
2. **Shareable Results**: Save and share evaluation reports with your team
3. **Audit Trail**: All results are timestamped and include configuration details
4. **No CLI Complexity**: Just run Python files directly

Results are also uploaded to LangSmith for experiment tracking and further analysis.