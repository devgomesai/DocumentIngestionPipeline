

from pymilvus import MilvusClient
from dotenv import load_dotenv
import os

load_dotenv()


milvus_uri = os.getenv("MILVUS_ENDPOINT")
token = os.getenv("MILVUS_TOKEN")

milvus_client = MilvusClient(uri=milvus_uri, token=token)

print(f"Connected to DB: {milvus_uri} successfully")
