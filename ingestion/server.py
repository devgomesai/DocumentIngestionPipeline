
import os
import shutil
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
    description="This servers as the API endpoint for this client to upload the files"
    
)

# Initializing the DBOS Client
client = DBOSClient(
    system_database_url=os.environ["DBOS_SYSTEM_DATABASE_URL"]
)

# Create the in memory dir to store the uploaded files
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

# Get the chat engine to test the 
chat_engine = get_chat_engine()


# Define the Chat Schema
class ChatSchema(BaseModel):
    message: str


# endpoint for uploading the files
@app.post("/file-upload")
async def file_upload(files: List[UploadFile] = File(...)):
    file_paths = []

    for file in files:
        path = UPLOAD_DIR / Path(file.filename).name
        with path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(str(path))

    # Create a queue and workflow Options
    options: EnqueueOptions = {
        "queue_name": "indexing-queue",
        "workflow_name": "index_uploaded_files",
    }
    # Enqueing the file paths and the Options
    client.enqueue(options, file_paths)
    
    
    return {"status": "indexing_started", "files": file_paths}


@app.post("/chat")
def chat(chat: ChatSchema):
    # Testing to make sure the files got ingested and responded based on the user query
    return {"response": str(chat_engine.chat(chat.message))}

