"""
Simple evaluation script: Naive vs Advanced Retriever.

Run this file directly to compare naive vs an advanced retriever.
Results are saved to results/evaluation_results.md
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from evaluation.evaluator import RAGEvaluator


def main():
    """Run evaluation comparing naive vs advanced retriever."""
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "LANGCHAIN_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
        print("Please set these in your .env file")
        return
    
    print("🚀 Starting RAG Evaluation: Naive vs Advanced")
    print("=" * 50)
    
    # Configuration
    advanced_retriever = "parent_document"  # Change this to test different retrievers
    test_size = 10  # Adjust test size as needed
    
    print(f"📊 Configuration:")
    print(f"   Advanced Retriever: {advanced_retriever}")
    print(f"   Test Size: {test_size}")
    print(f"   Output: results/evaluation_results.md")
    print()
    
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator()
        
        # Run comparison
        results_df = evaluator.evaluate_naive_vs_advanced(advanced_retriever, test_size)
        
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        # Generate markdown report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_content = f"""# RAG Evaluation Results
        
**Generated on:** {timestamp}  
**Comparison:** Naive vs {advanced_retriever.replace('_', ' ').title()}  
**Test Size:** {test_size} questions

## Results Summary

{results_df.to_markdown(index=False, floatfmt=".4f")}

## Analysis

"""
        
        if not results_df.empty and 'answer_relevancy' in results_df.columns:
            best_idx = results_df['answer_relevancy'].idxmax()
            best_retriever = results_df.loc[best_idx, 'retriever']
            best_score = results_df.loc[best_idx, 'answer_relevancy']
            
            markdown_content += f"""### Performance Comparison

| Metric | Naive | {advanced_retriever.replace('_', ' ').title()} | Winner |
|--------|-------|------------|---------|
"""
            
            naive_row = results_df[results_df['retriever'] == 'naive'].iloc[0]
            advanced_row = results_df[results_df['retriever'] == advanced_retriever].iloc[0]
            
            metrics = [
                ('Answer Relevancy', 'answer_relevancy', 'higher'),
                ('Context Recall', 'context_recall', 'higher'), 
                ('Faithfulness', 'faithfulness', 'higher'),
                ('Context Precision', 'context_precision', 'higher'),
                ('Latency (s)', 'avg_latency_s', 'lower'),
                ('Cost (USD)', 'total_cost_usd', 'lower')
            ]
            
            for metric_name, column, better in metrics:
                naive_val = naive_row[column]
                advanced_val = advanced_row[column]
                
                if better == 'higher':
                    winner = 'Naive' if naive_val > advanced_val else advanced_retriever.replace('_', ' ').title()
                else:
                    winner = 'Naive' if naive_val < advanced_val else advanced_retriever.replace('_', ' ').title()
                
                if metric_name == 'Cost (USD)':
                    markdown_content += f"| {metric_name} | ${naive_val:.4f} | ${advanced_val:.4f} | **{winner}** |\n"
                else:
                    markdown_content += f"| {metric_name} | {naive_val:.4f} | {advanced_val:.4f} | **{winner}** |\n"
            
            markdown_content += f"""
### Summary

| Aspect | Winner | Score/Value |
|--------|--------|-------------|
| **Best Overall Quality** | **{best_retriever}** | {best_score:.4f} relevancy |
| **Fastest Response** | **{results_df.loc[results_df['avg_latency_s'].idxmin(), 'retriever']}** | {results_df['avg_latency_s'].min():.2f}s |
| **Most Cost-Effective** | **{results_df.loc[results_df['total_cost_usd'].idxmin(), 'retriever']}** | ${results_df['total_cost_usd'].min():.4f} |"""
        
        markdown_content += f"""
## Configuration Details
- **CSV Path:** backend/data/feedback_corpus.csv
- **Evaluation Framework:** Custom RAG Evaluator with Ragas integration
- **Metrics:** Context Recall, Faithfulness, Answer Relevancy, Context Precision
- **Environment:** uv + Python virtual environment

## Notes
- All metrics are normalized between 0.0 and 1.0 (higher is better)
- Latency measured in seconds
- Cost represents OpenAI API usage in USD
"""
        
        # Save to results folder
        results_file = "results/evaluation_results.md"
        with open(results_file, 'w') as f:
            f.write(markdown_content)
        
        print(f"✅ Evaluation completed successfully!")
        print(f"📄 Results saved to: {results_file}")
        print(f"🏆 Best performer: {best_retriever} (Answer Relevancy: {best_score:.4f})")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()