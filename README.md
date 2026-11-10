# Academic Research Assistant

Agentic RAG platform for querying and synthesizing insights from arXiv machine learning research papers using hybrid vector-lexical retrieval and ReAct agent workflows.

---

## System Architecture

### Architectural Overview

```mermaid
flowchart TB
    subgraph Client["Client Interface"]
        UserQuery[User Request]
        WebUI[Next.js Web Application]
    end

    subgraph Service["Application Core"]
        FastAPIEndpoint[FastAPI Server]
        GraphWorkflow[LangGraph Agent Workflow]
    end

    subgraph Persistence["Storage & Indexes"]
        QdrantStore[Qdrant Vector Database]
        ElasticIndex[Elasticsearch BM25 Index]
    end

    subgraph SearchPipeline["Retrieval Pipeline"]
        HybridEngine[Hybrid Retrieval<br/>Dense + BM25 + RRF]
        CrossRerank[Cross-Encoder Reranker]























