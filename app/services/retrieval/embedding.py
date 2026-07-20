from vertexai.language_models import TextEmbeddingModel

model = None
BATCH_SIZE = 50
MAX_BATCH_TOKENS = 18000  # stay under Vertex's 20000 token-per-request cap

def get_embedding_model():
    global model
    if model is None:
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    return model

def embed_query(query:str):
    """Embeds single query string using vertex ai

    Args:
        query (str): single query
    """
    model = get_embedding_model()
    embedding = model.get_embeddings([query])
    return embedding[0].values

def _make_batches(texts: list[str], model) -> list[list[str]]:
    token_counts = [model.count_tokens([text]).total_tokens for text in texts]

    batches = []
    current_batch: list[str] = []
    current_tokens = 0

    for text, tokens in zip(texts, token_counts):
        exceeds_batch_size = len(current_batch) >= BATCH_SIZE
        exceeds_token_budget = current_batch and current_tokens + tokens > MAX_BATCH_TOKENS

        if exceeds_batch_size or exceeds_token_budget:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

        current_batch.append(text)
        current_tokens += tokens

    if current_batch:
        batches.append(current_batch)

    return batches

def embed_text(texts:list[str] ):
    """Embed list of text sting in batches, staying under Vertex's per-request token cap

    Args:
        texts (list[str]): list of text
    """

    model = get_embedding_model()
    all_embeddings = []
    for batch in _make_batches(texts, model):
        embeddings = model.get_embeddings(batch)
        all_embeddings.extend([e.values for e in embeddings])
    return all_embeddings