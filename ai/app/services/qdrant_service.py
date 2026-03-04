import logging

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


def check_health(client: QdrantClient) -> bool:
    try:
        client.get_collections()
        return True
    except Exception:
        logger.warning("Qdrant health check failed", exc_info=True)
        return False


def ensure_collection(client: QdrantClient) -> None:
    collection_name = settings.qdrant_collection
    try:
        client.get_collection(collection_name)
        logger.info("Collection '%s' already exists", collection_name)
    except (UnexpectedResponse, Exception):
        logger.info("Creating collection '%s'", collection_name)
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.embedding_dimension,
                distance=Distance.COSINE,
            ),
        )
        logger.info("Collection '%s' created", collection_name)


def upsert_embedding(
    client: QdrantClient,
    chunk_id: int,
    document_id: int,
    vector: list[float],
    text: str,
    chunk_index: int | None = None,
    start_pos: int | None = None,
    end_pos: int | None = None,
) -> None:
    payload: dict = {"document_id": document_id, "chunk_id": chunk_id, "text": text}
    if chunk_index is not None:
        payload["chunk_index"] = chunk_index
    if start_pos is not None:
        payload["start_pos"] = start_pos
    if end_pos is not None:
        payload["end_pos"] = end_pos

    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[PointStruct(id=chunk_id, vector=vector, payload=payload)],
    )


def batch_upsert_embeddings(
    client: QdrantClient,
    points: list[PointStruct],
) -> None:
    """여러 포인트를 한 번에 Qdrant에 적재. 단건 upsert보다 효율적."""
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )


def delete_embedding(client: QdrantClient, document_id: int) -> None:
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
    )


def search_embeddings(
    client: QdrantClient,
    query_vector: list[float],
    top_k: int = 5,
) -> list[ScoredPoint]:
    return client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )
