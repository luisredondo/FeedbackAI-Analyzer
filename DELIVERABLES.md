# Certification Challenge Submission

Hey\! Here are all the deliverables for the Mid-Bootcamp Certification Challenge. This document walks through the AI Product Management and AI Engineering decisions made for the **Client Feedback Analyzer** project.

-----

## ✅ Task 1: Defining your Problem and Audience

### Succinct 1-Sentence Problem Description

Product teams are drowning in unstructured user feedback from dozens of sources, making it nearly impossible to efficiently find the critical insights needed to make informed product decisions.

### Why this is a Problem for our User

Our target user is a **Product Manager (PM)** at a mid-sized SaaS company. A huge part of their job is understanding the "voice of the customer" to prioritize features, fix bugs, and guide the product roadmap.

Currently, this PM is struggling. Feedback lives everywhere: support tickets in Zendesk, app reviews on the App Store, survey results in Google Sheets, and random feature requests from the sales team in Slack. To figure out what users are complaining about, they have to manually read through everything, copy-paste snippets into a spreadsheet, and try to spot trends. This process is slow, tedious, and prone to human error. They live in constant fear that they're missing a major recurring issue or failing to spot the next big feature request that could drive growth.

A few potential questions this PM is trying to answer constantly are:

  * "What are the top 3 complaints about the new dashboard feature we just launched?"
  * "Are more people asking for a dark mode or a calendar integration?"
  * "Show me all the negative feedback from enterprise users over the last month."
  * "What do users love most about our 'quick add' feature?"

-----

## ✅ Task 2: Propose a Solution

### Proposed Solution and "Better World"

Our solution is an intelligent **Client Feedback Analyzer**. It's a simple web application where the PM can ask natural language questions just like the ones above. In the background, an AI agent finds the most relevant pieces of feedback from a centralized knowledge base, analyzes them, and provides a direct, actionable answer.

In this "better world," our PM starts their week by asking, "What were the most common user complaints last week?" Instead of spending hours digging, they get a concise, summarized list in seconds. They can instantly spot a bug with the latest release, quantify the demand for a new feature, and walk into their sprint planning meeting with concrete, data-backed evidence. This tool doesn't just save them time; it empowers them to be more strategic, responsive, and confident in their product decisions, directly connecting user feedback to the development cycle.

### Tech Stack Choices

We chose a modern, production-grade stack that leverages the core concepts from the bootcamp:

  * **LLM:** **OpenAI GPT-4o-mini** - It offers a fantastic balance of strong reasoning capabilities, speed, and cost-efficiency, making it perfect for both the RAG chain and the agent's decision-making process.
  * **Embedding Model:** **OpenAI text-embedding-3-small** - This is a powerful and highly cost-effective model for creating the vector embeddings that power our semantic search.
  * **Orchestration:** **LangChain & LangGraph** - This is the core of the application. We use LangChain for its robust components (loaders, splitters, retrievers) and LangGraph to build the stateful, multi-step agent that can decide which tool to use.
  * **Vector Database:** **Qdrant** - We started with an in-memory instance of Qdrant because it's incredibly fast for prototyping, easy to use, and can be seamlessly scaled to a cloud-based instance for production.
  * **Monitoring:** **LangSmith** - It's absolutely essential. LangSmith gives us deep visibility into every step of our agent's process, making debugging, evaluation, and tracking costs trivial.
  * **Evaluation:** **Ragas** - For quantitative evaluation, Ragas is the industry standard. It allows us to score our RAG pipeline on key metrics like context recall and faithfulness, so we can prove that our improvements actually work.
  * **User Interface:** **Streamlit** (Planned) - While we focused on the backend first, Streamlit is the clear choice for building a simple, interactive UI quickly so our PM can start using the tool ASAP.

### Use of Agentic Reasoning

We use an agent built with **LangGraph** to serve as the main "brain" of our application. Instead of having a static RAG pipeline, the agent dynamically decides the best way to answer a user's query.

For instance, if the PM asks, `"What are our competitors doing about AI features?"`, the agent's reasoning would identify that the answer isn't in our internal feedback data. It would then choose to use the **`web_search_tool` (Tavily)** to search the internet. Conversely, for a query like `"Show me complaints about the dashboard,"` the agent knows to use the **`feedback_search_tool`** to query our internal RAG pipeline. This agentic layer makes our application far more flexible and powerful than a simple RAG chain.

-----

## ✅ Task 3: Dealing with the Data

### Data Sources and External APIs

1.  **Primary Data Source (for RAG):** Our core data source is `backend/data/feedback_corpus.csv`. This file simulates a real-world collection of user feedback, containing columns like `source`, `date`, `feedback_text`, and `sentiment`. We generated this data synthetically using our `scripts/generate_data.py` script to ensure we had a realistic and varied corpus to build upon.
2.  **External API:** We are using the **Tavily Search API** as our agent's external tool for general web searches. This allows our application to answer questions that go beyond our internal feedback data, such as market trends, competitor analysis, or general knowledge questions.

### Default Chunking Strategy

Our default chunking strategy, implemented in `backend/agentic_rag.py`, is the **`RecursiveCharacterTextSplitter`** from LangChain.

We chose this because it's robust and intelligent. It tries to split text along semantic boundaries by working through a priority list of separators (like `\n\n`, `\n`, `     `). For unstructured data like user feedback, which can range from a single sentence to multiple paragraphs, this method is more effective at keeping related ideas together within a single chunk than a simple fixed-size character splitter.

-----

## ✅ Task 4: Building a Quick End-to-End Agentic RAG Prototype

We have successfully built an end-to-end prototype and deployed it to a local endpoint.

The entire backend is contained within the `backend/` directory. It can be started by running:

```bash
uvicorn backend.main:app --reload
```

This serves a FastAPI application, and its core logic is defined in `backend/agentic_rag.py`. It exposes an `/analyze` endpoint that takes a user query and processes it through our LangGraph agent, which is fully capable of using either its RAG tool or its web search tool.

-----

## ✅ Task 5: Creating a Golden Test Data Set

As an Evaluation & Performance Engineer, we created a "Golden Data Set" to baseline our system's performance. The entire process is documented in the `notebooks/02_evaluation.ipynb` notebook.

We used the `Ragas` library's `TestsetGenerator` to synthetically generate a high-quality test set of 15 question/answer pairs from our source documents. This dataset was then uploaded to a LangSmith project for tracing and evaluation.

### Baseline Pipeline Assessment (Naive Retriever)

Here is the RAGAS output table for our initial, naive RAG pipeline.

| Metric            |   Score |
|:------------------|--------:|
| context\_recall    |  0.1250 |
| faithfulness      |  0.8458 |
| answer\_relevancy  |  0.7360 |
| context\_precision |  0.1223 |

### Conclusions on Baseline Performance

The baseline results reveal significant room for improvement. While the **faithfulness** score of 0.85 shows that our model is staying true to the provided context, the **context recall** of only 0.125 indicates that our basic vector search is missing many relevant documents. The **context precision** of 0.12 suggests we're retrieving a lot of irrelevant chunks, which dilutes the quality of information passed to the LLM. However, the **answer relevancy** score of 0.74 shows that when the system does have relevant context, it can generate reasonably relevant answers. This baseline clearly signals that our biggest opportunity for improvement is in **retrieval quality** - both finding more relevant documents and filtering out irrelevant ones.

-----

## ✅ Task 6: The Benefits of Advanced Retrieval

To improve our system, we tested a host of advanced retrieval techniques, all implemented and tested within `notebooks/02_evaluation.ipynb`.

### Planned Retrieval Techniques

  * **BM25:** This will be useful for catching keyword-specific queries that semantic search might miss.
  * **Multi-Query:** This will be useful for ambiguous user questions by generating multiple perspectives on the query to broaden the search.
  * **Parent-Document:** This will be useful for providing the LLM with more context by retrieving small, precise chunks but passing the full parent document to the model.
  * **Cohere Rerank:** This will be useful for improving precision by taking a larger set of documents and re-ranking them for relevance before passing them to the LLM.
  * **Ensemble:** This will be useful for getting the best of both worlds by combining keyword-based search (BM25) and semantic search.

-----

## ✅ Task 7: Assessing Performance

It's time to assess all options for this product.

### Performance Comparison

Here is the final results table comparing our naive RAG application against the advanced retrieval methods. The metrics were collected using Ragas and LangSmith in our evaluation framework.

| Retriever       |   Context Recall |   Faithfulness |   Answer Relevancy |   Context Precision |   Avg. Latency (s) |   Total Cost ($) |
|:----------------|-----------------:|---------------:|-------------------:|--------------------:|-------------------:|-----------------:|
| Naive           |           0.1250 |         0.8458 |             **0.7360** |              0.1223 |             3.2728 |           0.0026 |
| BM25            |           **0.1667** |         0.8344 |             0.7069 |              **0.1458** |             **1.9550** |           **0.0019** |
| Multi-Query     |           0.1250 |         0.7188 |             0.7145 |              0.1087 |             7.3042 |           0.0054 |
| Parent-Document |           **0.2083** |         0.7222 |             0.5367 |              0.0833 |             **1.7796** |           **0.0006** |
| Ensemble        |           **0.1667** |         0.8156 |             0.6298 |              0.0576 |             2.6602 |           0.0029 |

### Articulating Changes and Future Improvements

The evaluation results reveal interesting insights about our retrieval strategies. While all approaches show relatively low context recall scores (indicating room for improvement in finding relevant documents), there are clear performance patterns:

**Key Findings:**
- **Naive Retriever** achieved the highest **Answer Relevancy** (0.7360), making it surprisingly effective at generating relevant responses despite lower recall
- **Parent-Document** strategy offers the best **Context Recall** (0.2083) and is significantly faster (1.78s) and more cost-effective ($0.0006)
- **BM25** provides a good balance with improved precision (0.1458) and excellent speed (1.96s) at low cost
- **Multi-Query** shows promise but comes with significantly higher latency (7.30s) and cost
- **Rerank** encountered technical issues during evaluation and needs debugging before implementation

**Strategic Decision:**
Given that our PM users need reliable, fast responses, we're taking a pragmatic approach. The **Naive Retriever** actually performs best for answer relevancy, which is most important for user experience. However, for production deployment, we'll implement a hybrid strategy using **Parent-Document** for speed-critical queries and **Naive** for quality-critical analysis.

For the next phase of development, our plan is to:

1.  **Debug and Implement Rerank:** Resolve the technical issues with Cohere Rerank as it has the highest theoretical potential
2.  **Build the Next.js Frontend:** Complete the modern chat interface for seamless PM interaction
3.  **Add Conversation Memory:** Enhance our LangGraph agent to maintain context across queries
4.  **Performance Optimization:** Focus on improving context recall across all retrievers through better chunking strategies