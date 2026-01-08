
import os
import shutil
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from dbos import DBOSClient, EnqueueOptions

from .index import get_chat_engine

load_dotenv(".env")

app = FastAPI()

# DBOS client (NO execution)
client = DBOSClient(
    system_database_url=os.environ["DBOS_SYSTEM_DATABASE_URL"]
)

UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

chat_engine = get_chat_engine()


class ChatSchema(BaseModel):
    message: str


@app.post("/file-upload")
async def file_upload(files: List[UploadFile] = File(...)):
    file_paths = []

    for file in files:
        path = UPLOAD_DIR / Path(file.filename).name
        with path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(str(path))

    options: EnqueueOptions = {
        "queue_name": "indexing-queue",
        "workflow_name": "index_uploaded_files",
    }

    client.enqueue(options, file_paths)

    return {"status": "indexing_started", "files": file_paths}


@app.post("/chat")
def chat(chat: ChatSchema):
    return {"response": str(chat_engine.chat(chat.message))}


@app.get("/")
def frontend():
    with open("html/app.html") as f:
        return HTMLResponse(f.read())
