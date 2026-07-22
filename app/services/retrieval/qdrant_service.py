import logfire
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import settings
from app.services.retrieval.embedding import get_embedding_model, embed_query

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

def search_enterprise_knowledge(query: str, limit: int = 10):
    """
    Searches the Qdrant vector database for relevant documents based on the query.
    """
    try:
        query_vector = embed_query(query)
        response = client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            limit=limit,
            with_payload=True
        )

        result=[]

        for res in response.points:
            result.append({
                "content": res.payload.get("text", ""),
                "source": res.payload.get("source", "unknown"),
                "score": res.score
            })
        
        return result
    except Exception as e:
        logfire.error(f"Error during Qdrant search: {e}")
        return []
    