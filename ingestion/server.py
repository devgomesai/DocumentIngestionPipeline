import os
import uuid
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from dbos import DBOSClient, EnqueueOptions

from .index import get_chat_engine

load_dotenv(".env")

app = FastAPI(
    title="📃 Document Ingestion Pipeline (Client)",
    description="API for uploading documents and enqueueing ingestion jobs",
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

# Set the chat engine 
_chat_engine = None

# get the chat engine
def engine():
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = get_chat_engine()
    return _chat_engine

# Define the Chat Schema (test)
class ChatSchema(BaseModel):
    message: str

# Endpoint for uploading one or more files
@app.post("/file-upload")
async def file_upload(files: List[UploadFile] = File(...)):
    workflow_ids = []
    file_paths = []

    # Options used to enqueue workflows into DBOS
    # Each enqueue call creates a new workflow execution
    options: EnqueueOptions = {
        "queue_name": INDEXING_QUEUE,
        "workflow_name": INDEX_WORKFLOW,
    }

    # Process each uploaded file independently
    for file in files:
        # Generate a unique filename to avoid collisions
        filename = f"{uuid.uuid4()}_{file.filename}"

        # Persist the uploaded file to local storage
        path = UPLOAD_DIR / filename
        path.write_bytes(await file.read())

        # Keep track of saved file paths
        file_paths.append(str(path))

        # Enqueue the workflow for this file
        # Each file becomes its own workflow execution
        handle = client.enqueue(options, [str(path)])

        # Store workflow ID for tracking/debugging
        workflow_ids.append(handle.workflow_id)

    # Return metadata to the client
    return {
        "status": "indexing_started",
        "workflow_ids": workflow_ids,
        "files": file_paths,
    }


# Endpoint to test querying the indexed documents
@app.post("/chat")
def chat(chat: ChatSchema):
    response = engine().chat(chat.message)
    return {"response": str(response)}
