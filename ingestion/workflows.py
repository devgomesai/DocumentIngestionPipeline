
from typing import List
from dbos import DBOS, Queue

from .steps import parse_uploaded_file, index_page


Queue("indexing-queue")

WF_PROGRESS_KEY = "ingestion_progress"


@DBOS.workflow()
def index_uploaded_files(file_paths: List[str]):
    progress = {
        "total_files": len(file_paths),
        "processed_files": 0,
        "status": "running",
    }

    DBOS.set_event(WF_PROGRESS_KEY, progress)

    total_docs = 0

    for file_path in file_paths:
        documents = parse_uploaded_file(file_path)
        for doc in documents:
            index_page(doc)
        total_docs += len(documents)

        progress["processed_files"] += 1
        DBOS.set_event(WF_PROGRESS_KEY, progress)

    progress["status"] = "completed"
    progress["total_documents"] = total_docs
    DBOS.set_event(WF_PROGRESS_KEY, progress)

    print(f"[WORKFLOW] Indexed {total_docs} documents")
