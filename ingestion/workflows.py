
from typing import List
from dbos import DBOS, Queue

from .steps import parse_uploaded_file, index_page


# The Queue that each worker is going to work on
Queue("indexing-queue")

# Identifier
WF_PROGRESS_KEY = "ingestion_progress"


@DBOS.workflow()
def index_uploaded_files(file_paths: List[str]):
    # Workflow that runs the pipeline
    progress = {
        "total_files": len(file_paths),
        "processed_files": 0,
        "status": "running",
    }
    # Set a workflow event
    DBOS.set_event(WF_PROGRESS_KEY, progress)

    total_docs = 0

    # Process for each files uploaded
    for file_path in file_paths:
        # documents from Docling Ingestor
        documents = parse_uploaded_file(file_path)
        for doc in documents:
            # index those doc from documents
            index_page(doc)
        total_docs += len(documents)

        # Update the Progress
        progress["processed_files"] += 1
        # Set the new event Progress
        DBOS.set_event(WF_PROGRESS_KEY, progress)

    # Once done set completed
    progress["status"] = "completed"
    progress["total_documents"] = total_docs
    
    # Update the Progress
    DBOS.set_event(WF_PROGRESS_KEY, progress)

    # Logging the number of docs processed via the workflow
    print(f"[WORKFLOW] Indexed {total_docs} documents")
