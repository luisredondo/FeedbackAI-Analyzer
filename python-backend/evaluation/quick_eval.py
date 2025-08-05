"""
Quick evaluation script for testing the system.

Run this file directly for a fast evaluation with minimal setup.
Results are printed to console only.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from evaluation.evaluator import RAGEvaluator


def quick_eval_naive_vs_advanced(advanced_retriever: str = "parent_document", test_size: int = 8):
    """Quick evaluation of naive vs advanced retriever."""
    # Load environment
    load_dotenv()
    
    print(f"🔍 Quick Evaluation: Naive vs {advanced_retriever.title()}")
    print(f"📊 Test size: {test_size}")
    
    # Initialize and run evaluation
    evaluator = RAGEvaluator()
    results_df = evaluator.evaluate_naive_vs_advanced(advanced_retriever, test_size)
    
    print("\\n" + "="*50)
    print("QUICK RESULTS")
    print("="*50)
    print(results_df.round(4).to_string(index=False))
    print("="*50)
    
    return results_df


def main():
    """Main function for running quick evaluation."""
    # Load environment
    load_dotenv()
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "LANGCHAIN_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
        print("Please set these in your .env file")
        return
    
    print("⚡ Quick RAG Evaluation")
    print("=" * 30)
    
    # Run quick comparison
    results = quick_eval_naive_vs_advanced("bm25", test_size=6)
    
    if not results.empty and 'answer_relevancy' in results.columns:
        try:
            # Filter out rows with errors and non-numeric values
            valid_results = results.dropna(subset=['answer_relevancy'])
            if not valid_results.empty:
                best_idx = valid_results['answer_relevancy'].idxmax()
                best_retriever = valid_results.loc[best_idx, 'retriever']
                best_score = valid_results.loc[best_idx, 'answer_relevancy']
                print(f"\\n🏆 Best performer: {best_retriever} (Score: {best_score:.4f})")
            else:
                print("\\n⚠️ No valid results to compare")
        except Exception as e:
            print(f"\\n⚠️ Could not determine best performer: {e}")


if __name__ == "__main__":
    main()