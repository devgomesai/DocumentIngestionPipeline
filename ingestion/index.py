
# ingestion/index.py
import os
from dotenv import load_dotenv

from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.vector_stores.postgres import PGVectorStore

load_dotenv()

Settings.chunk_size = 512

_vector_store = None
_index = None


def _create_vector_store() -> PGVectorStore:
    
    return PGVectorStore.from_params(
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=5432,
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        table_name="llamaindex_vectors",
        embed_dim=1536,
        perform_setup=True,  # safe: only once per process
    )


def get_index() -> VectorStoreIndex:
    """
    Used by DBOS workers and API
    Lazy + singleton per process
    """
    global _vector_store, _index

    if _index is None:
        _vector_store = _create_vector_store()

        storage_context = StorageContext.from_defaults(
            vector_store=_vector_store
        )

        _index = VectorStoreIndex(
            nodes=[],
            storage_context=storage_context,
        )

        print("=== pgvector index initialized ===")

    return _index


def get_chat_engine() -> BaseChatEngine:
    """
    API-only helper
    """
    index = get_index()
    return index.as_chat_engine()