# RAG Systems Field Guide

## What is Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) combines a retriever with a generator so that a language model can answer questions using information it was never trained on. Instead of relying purely on parametric memory, the model is given relevant passages at inference time.

RAG systems are popular because they let you update knowledge without retraining a model — you simply re-index new documents. They also reduce hallucination by grounding answers in retrieved text, and they let you cite sources for every claim the model makes.

## Vector Databases

A vector database stores embeddings alongside metadata and supports fast approximate nearest-neighbor search over millions or billions of vectors. Popular choices include Pinecone, Weaviate, Qdrant, Milvus, and pgvector for teams that want to stay on Postgres.

Most vector databases support hybrid search, combining a dense vector similarity score with a sparse keyword score (like BM25), which tends to outperform pure vector search on queries that contain rare terms, product codes, or exact phrases.

Filtering is a core vector database feature: attaching metadata such as `source`, `category`, or `date` to each vector lets you restrict a similarity search to a subset of the index before or after computing distances, which is essential once a corpus mixes multiple document types or sensitivity levels.

## Embedding Models

An embedding model maps text into a dense vector such that semantically similar text ends up close together in vector space. Sentence-transformers models like `all-MiniLM-L6-v2` are small and run locally; hosted options like OpenAI's `text-embedding-3` or Voyage AI's models trade a network call for higher retrieval quality on harder domains.

Embedding model choice interacts with chunking: a model with a short max input length forces smaller chunks, and a domain-mismatched model (e.g. a general-purpose embedding model on dense legal text) can silently hurt retrieval quality in a way that's hard to detect without an evaluation set.

## Prompt Engineering for RAG

Once relevant chunks are retrieved, how they're assembled into the prompt matters. Putting the most relevant chunk first or last (models attend more to the beginning and end of long contexts — the "lost in the middle" effect) and explicitly asking the model to cite which chunk supports each claim both measurably improve answer quality.

It also helps to instruct the model to say "I don't know" when the retrieved chunks don't contain the answer, rather than falling back on parametric knowledge that may be outdated or simply wrong for the domain.

## Evaluating RAG Systems

RAG evaluation typically covers two layers: retrieval quality (did we fetch the right chunks — measured with metrics like recall@k and MRR) and generation quality (given the right chunks, did the model produce a correct, well-grounded answer — measured with faithfulness and answer-relevance scores, often via an LLM-as-judge).

A common mistake is only evaluating the final answer. If retrieval silently regresses — for example after a chunking strategy change — end-to-end answer quality can still look fine on easy queries while failing badly on harder ones, so retrieval metrics should be tracked separately from generation metrics.
