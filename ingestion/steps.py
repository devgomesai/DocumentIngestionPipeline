# ingestion/steps.py
import os
from dbos import DBOS
from llama_index.core import Document
from llama_index.readers.docling import DoclingReader

from .index import get_index

docling_reader = DoclingReader()


@DBOS.step()
def parse_uploaded_file(file_path: str):
    print(f"[WORKER {os.getpid()}] Parsing {file_path}")
    return docling_reader.load_data(file_path=file_path)


@DBOS.step()
def index_page(page: Document):
    index = get_index()
    index.insert(page)
