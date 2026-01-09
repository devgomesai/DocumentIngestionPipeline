from typing import List #nq00
from dbos import DBOS, Queue, WorkflowHandle

from .steps import parse_uploaded_file, index_and_store_docs

indexing_queue = Queue("indexing-queue")

WF_PROGRESS_KEY = "ingestion_progress"

# Worflow Process
@DBOS.workflow()
def index_uploaded_files(file_paths: List[str]):
    # Logging
    progress = {
        "total_files": len(file_paths),
        "processed_files": 0,
        "status": "running",
    }
    # Set the event
    DBOS.set_event(WF_PROGRESS_KEY, progress)
    # handles contains the list of workflows to process
    handles: List[WorkflowHandle] = []
    # initial docs are set to 0
    total_docs = 0

    # For each file in the list of files enqueue them in the queue with the func(index_single_file)
    for file_path in file_paths:
        handle = indexing_queue.enqueue(index_single_file, file_path)
        # Append the WorkflowHandle into the handles
        handles.append(handle)

    # For each handle get the document count and add them to the total docs processed
    for handle in handles:
        docs_count = handle.get_result()
        total_docs += docs_count

        # Increment the processed_files
        progress["processed_files"] += 1
        # Update the event
        DBOS.set_event(WF_PROGRESS_KEY, progress)
    # Set status to completed once done processing
    progress["status"] = "completed"
    # Set the total documents processed
    progress["total_documents"] = total_docs
    # Update the event
    DBOS.set_event(WF_PROGRESS_KEY, progress)

    print(f"[WORKFLOW] Indexed {total_docs} documents")


# Handles the indexing of each file
@DBOS.workflow()
def index_single_file(file_path: str) -> int:
    # Get the docs from ingetor(docling)
    documents = parse_uploaded_file(file_path)
    # Then for each doc in it index and store into the VectorDB
    for doc in documents:
        index_and_store_docs(doc)
    # Return the length of total docs processed
    return len(documents)
