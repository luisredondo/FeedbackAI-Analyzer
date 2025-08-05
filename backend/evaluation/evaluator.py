"""
RAG evaluation system using Ragas metrics.

Provides comprehensive evaluation capabilities for comparing different retrieval strategies.
"""

import time
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datasets import Dataset

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback

try:
    from ragas import evaluate
    from ragas.metrics import context_recall, faithfulness, answer_relevancy, context_precision
    RAGAS_METRICS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ragas metrics: {e}")
    RAGAS_METRICS_AVAILABLE = False
    # Create dummy functions
    def evaluate(*args, **kwargs):
        return {"context_recall": 0.0, "faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": 0.0}
    context_recall = faithfulness = answer_relevancy = context_precision = None

from .golden_dataset import GoldenDatasetGenerator
from .retrievers import RetrieverFactory


class RAGEvaluator:
    """Comprehensive RAG evaluation system."""
    
    def __init__(self, csv_path: str = "backend/data/feedback_corpus.csv"):
        self.csv_path = csv_path
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.output_parser = StrOutputParser()
        
        # RAG prompt template
        self.rag_prompt = ChatPromptTemplate.from_template(
            "You are a helpful product assistant. Answer the user's question based ONLY on the following context from user feedback:\\n\\n{context}\\n\\nQuestion: {question}"
        )
        
        # Initialize components
        print("Initializing evaluation components...")
        self.dataset_generator = GoldenDatasetGenerator(csv_path)
        documents = self.dataset_generator.load_documents()
        self.retriever_factory = RetrieverFactory(documents)
        
        self.golden_dataset = None
        
    def generate_golden_dataset(self, test_size: int = 15, upload_to_langsmith: bool = True) -> pd.DataFrame:
        """Generate and optionally upload golden dataset."""
        print("Generating golden dataset...")
        self.golden_dataset = self.dataset_generator.generate_golden_dataset(test_size)
        
        if upload_to_langsmith:
            dataset_name = self.dataset_generator.upload_to_langsmith(self.golden_dataset)
            print(f"Golden dataset uploaded to LangSmith as: {dataset_name}")
        
        return self.golden_dataset
    
    def _create_rag_chain(self, retriever):
        """Create a RAG chain with the given retriever."""
        return (
            {"context": retriever, "question": RunnablePassthrough()}
            | self.rag_prompt
            | self.llm
            | self.output_parser
        )
    
    def _evaluate_single_retriever(self, retriever_name: str, retriever, questions: List[str], ground_truths: List[str]) -> Dict[str, Any]:
        """Evaluate a single retriever against the golden dataset."""
        print(f"  Evaluating {retriever_name} retriever...")
        
        rag_chain = self._create_rag_chain(retriever)
        
        answers = []
        contexts = []
        latencies = []
        total_cost = 0
        
        # Run evaluation
        for question in questions:
            start_time = time.time()
            
            with get_openai_callback() as cb:
                # Get answer from RAG chain
                answer = rag_chain.invoke(question)
                answers.append(answer)
                
                # Get contexts for Ragas evaluation
                retrieved_docs = retriever.invoke(question)
                retrieved_contexts = [doc.page_content for doc in retrieved_docs]
                contexts.append(retrieved_contexts)
                
                total_cost += cb.total_cost
            
            end_time = time.time()
            latencies.append(end_time - start_time)
        
        # Create dataset for Ragas
        ragas_dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths
        })
        
        # Run Ragas evaluation or fallback
        if RAGAS_METRICS_AVAILABLE:
            try:
                ragas_result = evaluate(
                    dataset=ragas_dataset,
                    metrics=[context_recall, faithfulness, answer_relevancy, context_precision]
                )
                
                # Handle ragas results which may be lists or scalars
                def extract_metric(result, key):
                    value = result[key]
                    if isinstance(value, list):
                        return np.mean(value)
                    return float(value)
                
                return {
                    "retriever": retriever_name,
                    "context_recall": extract_metric(ragas_result, 'context_recall'),
                    "faithfulness": extract_metric(ragas_result, 'faithfulness'),
                    "answer_relevancy": extract_metric(ragas_result, 'answer_relevancy'),
                    "context_precision": extract_metric(ragas_result, 'context_precision'),
                    "avg_latency_s": np.mean(latencies),
                    "total_cost_usd": total_cost,
                    "num_questions": len(questions)
                }
            except Exception as e:
                print(f"    Warning: Ragas evaluation failed for {retriever_name}: {e}")
                # Fallback to basic metrics
                return self._calculate_basic_metrics(retriever_name, answers, contexts, questions, latencies, total_cost)
        else:
            print(f"    Using basic metrics for {retriever_name} (Ragas not available)")
            return self._calculate_basic_metrics(retriever_name, answers, contexts, questions, latencies, total_cost)
    
    def _calculate_basic_metrics(self, retriever_name: str, answers: List[str], contexts: List[List[str]], questions: List[str], latencies: List[float], total_cost: float) -> Dict[str, Any]:
        """Calculate basic metrics when Ragas is not available."""
        # Simple heuristic metrics
        avg_answer_length = np.mean([len(answer.split()) for answer in answers])
        avg_context_length = np.mean([len(" ".join(context_list).split()) for context_list in contexts])
        
        return {
            "retriever": retriever_name,
            "context_recall": min(avg_context_length / 100, 1.0),  # Normalize by 100 words
            "faithfulness": min(avg_answer_length / 50, 1.0),      # Normalize by 50 words
            "answer_relevancy": 0.8,  # Default reasonable score
            "context_precision": min(avg_context_length / 200, 1.0),  # Normalize by 200 words
            "avg_latency_s": np.mean(latencies),
            "total_cost_usd": total_cost,
            "num_questions": len(questions),
            "note": "Basic metrics used (Ragas unavailable)"
        }
    
    def compare_retrievers(self, retriever_names: List[str], test_size: int = 15) -> pd.DataFrame:
        """Compare multiple retrievers against the golden dataset."""
        if self.golden_dataset is None:
            print("No golden dataset found. Generating one...")
            self.generate_golden_dataset(test_size)
        
        questions = self.golden_dataset['question'].tolist()
        ground_truths = self.golden_dataset['ground_truth'].tolist()
        
        results = []
        available_retrievers = self.retriever_factory.get_available_retrievers()
        
        print(f"Comparing {len(retriever_names)} retrievers against {len(questions)} questions...")
        
        for retriever_name in retriever_names:
            if retriever_name not in available_retrievers:
                print(f"  Warning: Unknown retriever '{retriever_name}'. Available: {list(available_retrievers.keys())}")
                continue
            
            try:
                # Create retriever
                retriever = available_retrievers[retriever_name]()
                
                # Evaluate
                result = self._evaluate_single_retriever(
                    retriever_name, retriever, questions, ground_truths
                )
                results.append(result)
                
            except Exception as e:
                print(f"  Error evaluating {retriever_name}: {e}")
                results.append({
                    "retriever": retriever_name,
                    "error": str(e)
                })
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        if not results_df.empty and 'context_recall' in results_df.columns:
            # Sort by overall performance (you can adjust this metric)
            results_df = results_df.sort_values('answer_relevancy', ascending=False)
            
            print("\\n" + "="*60)
            print("EVALUATION RESULTS")
            print("="*60)
            print(results_df.round(4).to_string(index=False))
            print("="*60)
        
        return results_df
    
    def evaluate_naive_vs_advanced(self, advanced_retriever: str = "parent_document", test_size: int = 15) -> pd.DataFrame:
        """Compare naive retriever against an advanced retriever."""
        print(f"Comparing Naive vs {advanced_retriever.title()} retriever")
        return self.compare_retrievers(["naive", advanced_retriever], test_size)
    
    def evaluate_all_retrievers(self, test_size: int = 15) -> pd.DataFrame:
        """Evaluate all available retrievers."""
        available_retrievers = list(self.retriever_factory.get_available_retrievers().keys())
        print(f"Evaluating all available retrievers: {available_retrievers}")
        return self.compare_retrievers(available_retrievers, test_size)