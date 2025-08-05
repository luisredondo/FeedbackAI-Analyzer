# Client Feedback Analyzer - Python Backend

FastAPI backend with LangChain + LangGraph Agentic RAG system for intelligent customer feedback analysis.

## Features

- **Agentic RAG System**: Uses LangGraph to orchestrate intelligent decision-making
- **FastAPI Backend**: RESTful API with CORS support for frontend integration
- **Vector Store Integration**: Qdrant for efficient similarity search
- **OpenAI Integration**: GPT-4o-mini and text-embedding-3-small
- **Web Search Capability**: Tavily integration for external knowledge
- **Comprehensive Evaluation Framework**: Multiple retrieval strategies with RAGAS metrics

## Quick Start

```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Generate synthetic data
uv run python scripts/generate_data.py

# Start the server
uv run uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /analyze` - Analyze feedback queries
- `GET /dataset-info` - Get dataset information
- `GET /health` - Health check
- `GET /docs` - Swagger documentation

## Evaluation Framework

```bash
# Quick evaluation
uv run python evaluation/quick_eval.py

# Compare naive vs advanced retriever
uv run python evaluation/run_naive_vs_advanced.py

# Full evaluation of all retrievers
uv run python evaluation/run_all_retrievers.py
```

Results are saved to `results/` as markdown reports.