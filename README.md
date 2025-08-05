# Client Feedback Analyzer

## DEMO VIDEO
🎥 [Watch the Demo](https://www.loom.com/share/2b516789b62e49589816364bdf6910b0?sid=bc4ac075-ecb8-4600-96e2-76e51b3e3cb6)

## 📋 Documentation
- [📄 Project Deliverables](DELIVERABLES.md) - Complete challenge submission and technical decisions
- [🔗 Merge Instructions](MERGE.md) - How to merge frontend and backend

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ with `uv` package manager
- Node.js 18+ with npm
- OpenAI API key
- Tavily API key

### Setup & Run
```bash
# Install dependencies
npm run install:all

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Generate synthetic data
cd python-backend && uv run python scripts/generate_data.py && cd ..

# Start both backend and frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🏗️ Architecture
- **Backend**: Python FastAPI + LangChain + LangGraph Agentic RAG
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Storage**: Qdrant vector store
- **AI**: OpenAI GPT-4o-mini + Tavily web search

## 📊 Evaluation Results
- [🔬 All Retrievers Results](python-backend/results/all_retrievers_results.md)

### Run Evaluations
```bash
cd python-backend

# Quick evaluation
uv run python evaluation/quick_eval.py

# Compare retrievers
uv run python evaluation/run_naive_vs_advanced.py

# Full evaluation suite
uv run python evaluation/run_all_retrievers.py
```

## 📁 Project Structure
```
├── python-backend/     # FastAPI + LangGraph backend
├── frontend/          # Next.js chat interface
├── DELIVERABLES.md    # Project documentation
└── MERGE.md          # Integration instructions
```

## 🛠️ Development
```bash
# Backend only
cd python-backend && PYTHONPATH=. uv run uvicorn backend.main:app --reload

# Frontend only
cd frontend && npm run dev
```

## 🔧 Troubleshooting
1. Ensure `.env` file exists with valid API keys
2. Check backend health: `curl http://localhost:8000/health`
3. Verify both services are running on correct ports# FeedbackAI-Analyzer
