
import os
from dbos import DBOS
from llama_index.core import Document
from llama_index.readers.docling import DoclingReader

from .index import get_index

# Creating the steps
@DBOS.step()
def parse_uploaded_file(file_path: str):
    # Initializing the Ingestor ( Docling ) 
    docling_reader = DoclingReader()
    # See which worker is working on which file
    print(f"[WORKER {os.getpid()}] Parsing {file_path}")
    # return the list of docs with data and uuid from the loaded file
    return docling_reader.load_data(file_path=file_path)


@DBOS.step()
def index_and_store_docs(page: Document):
    # Get the index and insert it into PgVector
    # print(page)
    """
    Doc ID: e3e5393d-73eb-4b6e-81bf-73a126d7f92e
Text: ## Infosys Ltd  infosys.com  1,613  -1.57%  08Jan-closeprice
BSE:500209  NSE:INFY  | Market Cap                     | 6,54,179Cr.
| Current Price                  | 1,613                          |
High / Low                     | 1,983 /1,307                   |
|--------------------------------|-----------------------------...
    """
    index = get_index()
    index.insert(page)
    print("=== Inserted document into pgvector index ===")