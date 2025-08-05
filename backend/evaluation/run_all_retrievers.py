"""
Comprehensive evaluation script: All Retrievers.

Run this file directly to evaluate all available retrievers.
Results are saved to results/all_retrievers_results.md
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from evaluation.evaluator import RAGEvaluator


def main():
    """Run evaluation comparing all available retrievers."""
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "LANGCHAIN_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
        print("Please set these in your .env file")
        return
    
    print("🚀 Starting Comprehensive RAG Evaluation: All Retrievers")
    print("=" * 60)
    
    # Configuration
    test_size = 12  # Adjust test size as needed
    
    print(f"📊 Configuration:")
    print(f"   Evaluating: All available retrievers")
    print(f"   Test Size: {test_size}")
    print(f"   Output: results/all_retrievers_results.md")
    print()
    
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator()
        
        # Run comprehensive evaluation
        results_df = evaluator.evaluate_all_retrievers(test_size)
        
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        # Generate comprehensive markdown report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_content = f"""# Comprehensive RAG Evaluation Results
        
**Generated on:** {timestamp}  
**Evaluation:** All Available Retrievers  
**Test Size:** {test_size} questions

## Available Retriever Strategies

1. **Naive** - Simple vector similarity search
2. **BM25** - Keyword-based search (BM25 algorithm)  
3. **Multi-Query** - Generates multiple queries for better recall
4. **Parent-Document** - Hierarchical chunking with parent-child relationships
5. **Rerank** - Uses Cohere to rerank retrieved documents
6. **Ensemble** - Combines BM25 and vector search

## Complete Results

{results_df.to_markdown(index=False, floatfmt=".4f")}

## Performance Analysis

"""
        
        if not results_df.empty and 'answer_relevancy' in results_df.columns:
            # Sort by answer relevancy for analysis
            sorted_df = results_df.sort_values('answer_relevancy', ascending=False)
            
            markdown_content += f"""### Ranking by Answer Relevancy

| Rank | Retriever | Answer Relevancy Score |
|------|-----------|------------------------|
"""
            for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
                markdown_content += f"| {i} | {row['retriever']} | {row['answer_relevancy']:.4f} |\n"
            
            markdown_content += f"""
### Speed vs Quality Trade-offs

| Retriever | Latency (s) | Cost (USD) | Answer Relevancy |
|-----------|-------------|------------|------------------|
"""
            for _, row in results_df.iterrows():
                markdown_content += f"| {row['retriever']} | {row['avg_latency_s']:.2f} | ${row['total_cost_usd']:.4f} | {row['answer_relevancy']:.3f} |\n"
            
            # Best performer analysis
            best_overall = sorted_df.iloc[0]
            fastest = results_df.loc[results_df['avg_latency_s'].idxmin()]
            cheapest = results_df.loc[results_df['total_cost_usd'].idxmin()]
            
            markdown_content += f"""
## Key Insights

### Performance Highlights

| Category | Retriever | Metric Value | Answer Relevancy |
|----------|-----------|--------------|------------------|
| 🏆 **Best Overall** | {best_overall['retriever']} | {best_overall['answer_relevancy']:.4f} | {best_overall['answer_relevancy']:.4f} |
| ⚡ **Fastest** | {fastest['retriever']} | {fastest['avg_latency_s']:.2f}s | {fastest['answer_relevancy']:.4f} |
| 💰 **Most Cost-Effective** | {cheapest['retriever']} | ${cheapest['total_cost_usd']:.4f} | {cheapest['answer_relevancy']:.4f} |

### Detailed Performance Breakdown

| Retriever | Latency (s) | Cost (USD) | Answer Relevancy | Context Recall | Faithfulness |
|-----------|-------------|------------|------------------|----------------|--------------|
"""
            for _, row in sorted_df.iterrows():
                markdown_content += f"| {row['retriever']} | {row['avg_latency_s']:.2f} | ${row['total_cost_usd']:.4f} | {row['answer_relevancy']:.4f} | {row['context_recall']:.4f} | {row['faithfulness']:.4f} |\n"
        
        markdown_content += f"""
## Methodology

### Evaluation Metrics
- **Context Recall:** How well the retriever finds relevant contexts
- **Faithfulness:** How accurately the answer reflects the retrieved context  
- **Answer Relevancy:** How relevant the answer is to the question
- **Context Precision:** How precise the retrieved contexts are

### Data & Setup
- **Dataset:** Synthetic feedback corpus (backend/data/feedback_corpus.csv)
- **Questions:** {test_size} generated test questions covering various feedback scenarios
- **Model:** GPT-4o-mini for answer generation
- **Embeddings:** OpenAI text-embedding-3-small

## Recommendations

| Use Case | Recommended Retriever | Rationale |
|----------|----------------------|-----------|
| **Production (Balanced)** | {sorted_df.iloc[0]['retriever']} | Best overall quality ({sorted_df.iloc[0]['answer_relevancy']:.3f} relevancy) |
| **High-Volume Apps** | {fastest['retriever']} | Fastest response time ({fastest['avg_latency_s']:.2f}s) |
| **Maximum Quality** | {sorted_df.iloc[0]['retriever']} | Highest answer relevancy score |
| **Budget-Conscious** | {cheapest['retriever']} | Lowest cost (${cheapest['total_cost_usd']:.4f}) |

### Decision Matrix

| Priority | Weight | Top Choice | Alternative |
|----------|--------|------------|-------------|
| **Quality First** | High | {sorted_df.iloc[0]['retriever']} | {sorted_df.iloc[1]['retriever'] if len(sorted_df) > 1 else 'N/A'} |
| **Speed First** | High | {fastest['retriever']} | {sorted_df.nsmallest(2, 'avg_latency_s').iloc[1]['retriever'] if len(sorted_df) > 1 else 'N/A'} |
| **Cost First** | High | {cheapest['retriever']} | {sorted_df.nsmallest(2, 'total_cost_usd').iloc[1]['retriever'] if len(sorted_df) > 1 else 'N/A'} |

## Configuration Details
- **Evaluation Framework:** Custom RAG Evaluator with Ragas integration
- **Environment:** uv + Python virtual environment
- **Vector Store:** Qdrant in-memory
- **Chunk Size:** 1000 characters with 100 overlap
"""
        
        # Save to results folder
        results_file = "results/all_retrievers_results.md"
        with open(results_file, 'w') as f:
            f.write(markdown_content)
        
        print(f"✅ Comprehensive evaluation completed successfully!")
        print(f"📄 Results saved to: {results_file}")
        if not results_df.empty:
            best_retriever = sorted_df.iloc[0]['retriever']
            best_score = sorted_df.iloc[0]['answer_relevancy']
            print(f"🏆 Best overall performer: {best_retriever} (Answer Relevancy: {best_score:.4f})")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()