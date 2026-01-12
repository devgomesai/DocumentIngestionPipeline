import os
from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.chat_engine.types import BaseChatEngine 
from llama_index.vector_stores.postgres import PGVectorStore
# import asyncio
# from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
# from llama_index.vector_stores.milvus.base import BM25BuiltInFunction

load_dotenv()


# Setting the Chunk Size ,Chunk Overlap, Embedding Model and the LLM model
Settings.chunk_size = 512
Settings.chunk_overlap = 50
Settings.embed_model =  OllamaEmbedding(
    model_name="nomic-embed-text:latest",
    base_url="http://localhost:11434",
)
Settings.llm = GoogleGenAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),  
)
# Set the vector_store and the index
_vector_store = None
_index = None

# Creating the vector Store => PGVectorStore

def _create_vector_store() -> PGVectorStore:
    return PGVectorStore.from_params(
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=5432,
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        table_name="llamaindex_vectors",
        embed_dim=768,
        perform_setup=True,
    )

# def _create_vector_store() -> MilvusVectorStore:
#     return MilvusVectorStore(
#         uri=os.getenv("MILVUS_ENDPOINT"),
#         token=os.getenv("MILVUS_TOKEN"),
#         collection_name=os.getenv("MILVUS_COLLECTION"),
#         dim=768,
#         overwrite=True,
#         enable_async=False,
#     )


# Creating the Index Retriever
def get_index() -> VectorStoreIndex:
    """
    Lazy singleton per process
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

        print("=== Milvus index initialized ===")

    return _index

# Creating the Chat engine
def get_chat_engine() -> BaseChatEngine:
    # Get the index
    index = get_index()
    return index.as_chat_engine(
        chat_mode="best",
        similarity_top_k=5,
    )
