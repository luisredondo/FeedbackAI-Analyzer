# Comprehensive RAG Evaluation Results
        
**Generated on:** 2025-08-05 15:25:49  
**Evaluation:** All Available Retrievers  
**Test Size:** 12 questions

## Available Retriever Strategies

1. **Naive** - Simple vector similarity search
2. **BM25** - Keyword-based search (BM25 algorithm)  
3. **Multi-Query** - Generates multiple queries for better recall
4. **Parent-Document** - Hierarchical chunking with parent-child relationships
5. **Rerank** - Uses Cohere to rerank retrieved documents
6. **Ensemble** - Combines BM25 and vector search

## Complete Results

| retriever       |   context_recall |   faithfulness |   answer_relevancy |   context_precision |   avg_latency_s |   total_cost_usd |   num_questions | error                                                                                                                                                                                                               |
|:----------------|-----------------:|---------------:|-------------------:|--------------------:|----------------:|-----------------:|----------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| naive           |           0.1250 |         0.8458 |             0.7360 |              0.1223 |          3.2728 |           0.0026 |         12.0000 | nan                                                                                                                                                                                                                 |
| multi_query     |           0.1250 |         0.7188 |             0.7145 |              0.1087 |          7.3042 |           0.0054 |         12.0000 | nan                                                                                                                                                                                                                 |
| bm25            |           0.1667 |         0.8344 |             0.7069 |              0.1458 |          1.9550 |           0.0019 |         12.0000 | nan                                                                                                                                                                                                                 |
| ensemble        |           0.1667 |         0.8156 |             0.6298 |              0.0576 |          2.6602 |           0.0029 |         12.0000 | nan                                                                                                                                                                                                                 |
| parent_document |           0.2083 |         0.7222 |             0.5367 |              0.0833 |          1.7796 |           0.0006 |         12.0000 | nan                                                                                                                                                                                                                 |
## Performance Analysis

### Ranking by Answer Relevancy

| Rank | Retriever | Answer Relevancy Score |
|------|-----------|------------------------|
| 1 | naive | 0.7360 |
| 2 | multi_query | 0.7145 |
| 3 | bm25 | 0.7069 |
| 4 | ensemble | 0.6298 |
| 5 | parent_document | 0.5367 |
| 6 | rerank | nan |

### Speed vs Quality Trade-offs

| Retriever | Latency (s) | Cost (USD) | Answer Relevancy |
|-----------|-------------|------------|------------------|
| naive | 3.27 | $0.0026 | 0.736 |
| multi_query | 7.30 | $0.0054 | 0.715 |
| bm25 | 1.96 | $0.0019 | 0.707 |
| ensemble | 2.66 | $0.0029 | 0.630 |
| parent_document | 1.78 | $0.0006 | 0.537 |
| rerank | nan | $nan | nan |

## Key Insights

### Performance Highlights

| Category | Retriever | Metric Value | Answer Relevancy |
|----------|-----------|--------------|------------------|
| 🏆 **Best Overall** | naive | 0.7360 | 0.7360 |
| ⚡ **Fastest** | parent_document | 1.78s | 0.5367 |
| 💰 **Most Cost-Effective** | parent_document | $0.0006 | 0.5367 |

### Detailed Performance Breakdown

| Retriever | Latency (s) | Cost (USD) | Answer Relevancy | Context Recall | Faithfulness |
|-----------|-------------|------------|------------------|----------------|--------------|
| naive | 3.27 | $0.0026 | 0.7360 | 0.1250 | 0.8458 |
| multi_query | 7.30 | $0.0054 | 0.7145 | 0.1250 | 0.7188 |
| bm25 | 1.96 | $0.0019 | 0.7069 | 0.1667 | 0.8344 |
| ensemble | 2.66 | $0.0029 | 0.6298 | 0.1667 | 0.8156 |
| parent_document | 1.78 | $0.0006 | 0.5367 | 0.2083 | 0.7222 |
| rerank | nan | $nan | nan | nan | nan |

## Methodology

### Evaluation Metrics
- **Context Recall:** How well the retriever finds relevant contexts
- **Faithfulness:** How accurately the answer reflects the retrieved context  
- **Answer Relevancy:** How relevant the answer is to the question
- **Context Precision:** How precise the retrieved contexts are

### Data & Setup
- **Dataset:** Synthetic feedback corpus (backend/data/feedback_corpus.csv)
- **Questions:** 12 generated test questions covering various feedback scenarios
- **Model:** GPT-4o-mini for answer generation
- **Embeddings:** OpenAI text-embedding-3-small

## Recommendations

| Use Case | Recommended Retriever | Rationale |
|----------|----------------------|-----------|
| **Production (Balanced)** | naive | Best overall quality (0.736 relevancy) |
| **High-Volume Apps** | parent_document | Fastest response time (1.78s) |
| **Maximum Quality** | naive | Highest answer relevancy score |
| **Budget-Conscious** | parent_document | Lowest cost ($0.0006) |

### Decision Matrix

| Priority | Weight | Top Choice | Alternative |
|----------|--------|------------|-------------|
| **Quality First** | High | naive | multi_query |
| **Speed First** | High | parent_document | bm25 |
| **Cost First** | High | parent_document | bm25 |

## Configuration Details
- **Evaluation Framework:** Custom RAG Evaluator with Ragas integration
- **Environment:** uv + Python virtual environment
- **Vector Store:** Qdrant in-memory
- **Chunk Size:** 1000 characters with 100 overlap
