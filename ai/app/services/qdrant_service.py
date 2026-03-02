import logging

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams

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
    document_id: int,
    vector: list[float],
) -> None:
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[
            PointStruct(
                id=document_id,
                vector=vector,
                payload={"document_id": document_id},
            )
        ],
    )


def delete_embedding(client: QdrantClient, document_id: int) -> None:
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=[document_id],
    )
