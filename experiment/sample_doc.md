# Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) combines a retriever with a generator so that a language model can answer questions using information it was never trained on. Instead of relying purely on parametric memory, the model is given relevant passages at inference time.

## Why Chunking Matters

Chunking is the process of splitting a large document into smaller pieces before embedding and indexing them. The size and boundaries of a chunk directly affect retrieval quality: chunks that are too large dilute the embedding with irrelevant content, while chunks that are too small lose the surrounding context a reader needs to make sense of them.

A good chunking strategy tries to balance three things:

- **Semantic coherence** — each chunk should represent one idea or topic.
- **Context preservation** — enough surrounding text should be kept that the chunk is understandable on its own.
- **Retrieval granularity** — chunks should be small enough that a similarity search can pinpoint the relevant passage without pulling in unrelated text.

## Naive Fixed-Size Splitting

The simplest approach slices text every N characters or tokens, regardless of sentence or paragraph boundaries.

```python
def naive_chunks(text, size=200):
    return [text[i:i+size] for i in range(0, len(text), size)]
```

This is fast and library-free, but it can cut sentences (and even words) in half, which hurts embedding quality.

## Structure-Aware Splitting

Better splitters respect the document's natural structure — paragraphs, sentences, Markdown headers, or HTML tags — before falling back to a hard character limit. Recursive splitters try a list of separators in order (for example `["\n\n", "\n", ". ", " "]`) and only fall back to a harder cut when a piece still exceeds the target size.

## Semantic Chunking

Semantic chunkers go one step further: they embed individual sentences, measure the similarity between consecutive sentences, and cut a new chunk wherever the topic shifts significantly. This tends to produce chunks that align with actual topic boundaries rather than arbitrary length limits, at the cost of needing an embedding model at chunking time.

## Choosing a Strategy

For most production RAG systems, a recursive character or token splitter with a modest overlap (10-20% of chunk size) is a strong default. Semantic and layout-aware chunkers are worth the extra cost when documents have highly variable structure (contracts, manuals, mixed HTML/PDF sources) or when retrieval quality on those documents is measurably poor with the simpler approach.
