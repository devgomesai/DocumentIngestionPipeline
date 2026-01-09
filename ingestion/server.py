
import os
from pathlib import Path
from typing import List
import uuid

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from dbos import DBOSClient, EnqueueOptions

from .index import get_chat_engine

load_dotenv(".env")

app = FastAPI(
    title="📃 Document Ingestion Pipeline (Client)",
    description="This servers as the API endpoint for this client to upload the files"
    
)

# Initializing the DBOS Client
client = DBOSClient(
    system_database_url=os.environ["DBOS_SYSTEM_DATABASE_URL"]
)

# Create the in memory dir to store the uploaded files
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

INDEXING_QUEUE = "indexing-queue"
INDEX_WORKFLOW = "index_uploaded_files"

# Get the chat engine to test the 
_chat_engine = None

def engine():
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = get_chat_engine()
    return _chat_engine


# Define the Chat Schema
class ChatSchema(BaseModel):
    message: str


# endpoint for uploading the files
@app.post("/file-upload")
async def file_upload(files: List[UploadFile] = File(...)):
    file_paths = []

    for file in files:
        filename = f"{uuid.uuid4()}_{file.filename}"
        path = UPLOAD_DIR / filename
        path.write_bytes(await file.read())
        file_paths.append(str(path))

    options: EnqueueOptions = {
        "queue_name": INDEXING_QUEUE,
        "workflow_name": INDEX_WORKFLOW,
    }

    handle = client.enqueue(options, file_paths)

    return {
        "status": "indexing_started",
        "workflow_id": handle.workflow_id,
        "files": file_paths,
    }



@app.post("/chat")
def chat(chat: ChatSchema):
    response = engine().chat(chat.message)
    return {"response": str(response)}

