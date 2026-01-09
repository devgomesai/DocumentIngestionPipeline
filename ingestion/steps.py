import os
from dbos import DBOS
from llama_index.core import Document
from llama_index.readers.docling import DoclingReader

from .index import get_index


# Ingestor Module for document reading (.jpeg, .pptx, .pdf, .mp3 ......) supported types
docling_reader = DoclingReader()


# Step for parsing the document into the ingestor (Docling)
@DBOS.step()
def parse_uploaded_file(file_path: str):
    # Logging the worker process id and the file it is working with
    print(f"[WORKER {os.getpid()}] Parsing {file_path}")
    # return the resposne from the ingestor
    return docling_reader.load_data(file_path=file_path)

# Set for creating indexing and embedding and then storing ito the PGVector
@DBOS.step()
def index_and_store_docs(page: Document):
    # Get the index  
    index = get_index()
    # store into the vectorDB
    index.insert(page)
    print(f"[INDEXED] doc_id={page.doc_id}")
