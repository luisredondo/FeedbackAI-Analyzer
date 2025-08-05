import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import config first to load environment variables
import backend.config as config
from backend.agent import FeedbackAnalyzer
from backend.models import QueryRequest, AnalysisResponse, HealthResponse

# Initialize FastAPI app
app = FastAPI(
    title="Client Feedback Analyzer API",
    description="An API for analyzing user feedback with an Agentic RAG system.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the feedback analyzer
analyzer = FeedbackAnalyzer()

# API endpoint
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_feedback(request: QueryRequest) -> AnalysisResponse:
    """
    Accepts a user query, processes it through the Agentic RAG system,
    and returns the final analysis.
    """
    response = await analyzer.analyze(request.query)
    return AnalysisResponse(response=response)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Health check endpoint for service monitoring."""
    return HealthResponse(status="ok")

@app.get("/dataset-info")
async def get_dataset_info():
    """Get information about the loaded dataset"""
    try:
        import os
        import csv
        from datetime import datetime
        
        csv_path = "backend/data/feedback_corpus.csv"
        
        if not os.path.exists(csv_path):
            return {
                "filename": "feedback_corpus.csv",
                "recordCount": 0,
                "lastUpdated": "Not found",
                "fileSize": "0 KB",
                "status": "File not found"
            }
        
        # Get file stats
        file_stats = os.stat(csv_path)
        file_size = file_stats.st_size
        last_modified = datetime.fromtimestamp(file_stats.st_mtime)
        
        # Count records
        record_count = 0
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                record_count = sum(1 for row in reader)
        except Exception:
            record_count = 0
        
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        return {
            "filename": "feedback_corpus.csv",
            "recordCount": record_count,
            "lastUpdated": last_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "fileSize": size_str,
            "status": "Loaded"
        }
        
    except Exception as e:
        return {
            "filename": "feedback_corpus.csv",
            "recordCount": 0,
            "lastUpdated": "Error",
            "fileSize": "Unknown",
            "status": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)