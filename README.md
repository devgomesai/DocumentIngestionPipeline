# DBOS Document Ingestion Pipeline

A highly scalable, durable, and reliable multi-document ingestion and Retrieval-Augmented Generation (RAG) system built with **DBOS**, **LlamaIndex**, and **FastAPI**.

## 🚀 Overview

DBOS Document Detective is designed to handle large-scale document processing with guaranteed reliability. By leveraging **DBOS (Database-Oriented Operating System)**, the system ensures that long-running ingestion tasks are durable, stateful, and can recover automatically from failures.

The application allows users to upload various document types (PDFs, CSVs, etc.), parses them using **Docling**, indexes them into a **PostgreSQL (pgvector)** vector store, and provides a conversational interface to query the document's content.

## 🏗️ Architecture

The system is split into two main components to ensure scalability and separation of concerns:

1. **API Server (FastAPI):**
   * Handles file uploads and chat requests.
   * Orchestrates workflows by enqueuing tasks to DBOS workers.
   * Serves the frontend interface.
2. **Distributed Workers (`workera.py`, `workerb.py`):**
   * Asynchronously process indexing tasks from the DBOS queue.
   * Perform document parsing and vector embedding.
   * Ensure "exactly-once" execution of indexing steps.

### Workflow Logic

- **`index_uploaded_files`**: A DBOS workflow that coordinates the parallel processing of multiple uploaded files.
- **`index_uploaded_file`**: A sub-workflow for processing a single file.
- **`parse_uploaded_file`**: A durable step that uses Docling to extract content.
- **`index_page`**: A durable step that inserts document nodes into the vector database.

## 🛠️ Tech Stack

* **Orchestration:** [DBOS](https://www.dbos.dev/) (Durable Workflows, Task Queues)
* **RAG Framework:** [LlamaIndex](https://www.llamaindex.ai/)
* **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Parsing:** [Docling](https://github.com/DS4SD/docling)
* **Database:** PostgreSQL with [pgvector](https://github.com/pgvector/pgvector) (Neon recommended)
* **Frontend:** Tailwind CSS, Marked.js

## ⚙️ Getting Started

### Prerequisites

* Python 3.13+
* PostgreSQL instance with `pgvector` enabled (e.g., [Neon.tech](https://neon.tech))
* [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd Dbos-tests
   ```
2. **Install dependencies:**
   Using `uv`:

   ```bash
   uv sync
   ```

   Or using `pip`:

   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Configuration:**
   Create a `.env` file in the root directory:

   ```env
   # DBOS Configuration
   DBOS_SYSTEM_DATABASE_URL=postgresql://user:password@host:port/dbname
   APPLICATION_NAME=RAG-ingestor

   # Database Configuration (Neon/pgvector)
   PGHOST=your-host.neon.tech
   PGUSER=your-user
   PGPASSWORD=your-password
   PGDATABASE=neondb

   # LLM Provider (e.g., OpenAI)
   OPENAI_API_KEY=your-api-key
   ```

### Running the Application

To run the full system, you need to start the API server and at least one worker.

1. **Start the API Server:**

   ```bash
   # Using uv
   uv run fastapi dev ingestion/main.py
   ```
2. **Start the Workers (in separate terminals):**

   ```bash
   python workera.py
   python workerb.py
   ```

## 📁 Project Structure

```text
.
├── data/               # Uploaded documents and reference assets
├── html/               # Frontend application files
├── ingestion/          # Core logic (FastAPI, LlamaIndex, DBOS)
│   ├── index.py        # Vector store & index configuration
│   └── main.py         # API endpoints and DBOS workflows
├── tests/              # Test assets and documentation
├── workera.py          # DBOS Worker instance A
├── workerb.py          # DBOS Worker instance B
├── dbos-config.yaml    # DBOS global configuration
└── pyproject.toml      # Project dependencies and metadata
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
