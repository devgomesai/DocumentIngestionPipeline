
import os
from dbos import DBOS
from llama_index.core import Document
from llama_index.readers.docling import DoclingReader

from .index import get_index


# Initializing the Ingestor ( Docling ) 
docling_reader = DoclingReader()


# Creating the steps
@DBOS.step()
def parse_uploaded_file(file_path: str):
    # See which worker is working on which file
    print(f"[WORKER {os.getpid()}] Parsing {file_path}")
    # return the list of docs with data and uuid from the loaded file
    return docling_reader.load_data(file_path=file_path)


@DBOS.step()
def index_page(page: Document):
    # Get the index and insert it into PgVector
    index = get_index()
    index.insert(page)
