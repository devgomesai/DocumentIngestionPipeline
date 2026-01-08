import os
import threading
from dotenv import load_dotenv
from dbos import DBOS

import ingestion.workflows  # noqa
import ingestion.steps      # noqa

load_dotenv(".env")

if __name__ == "__main__":
    DBOS(
        config={
            "name": os.getenv("APPLICATION_NAME", "llama-rag"),
            "system_database_url": os.environ["DBOS_SYSTEM_DATABASE_URL"],
            "conductor_key": os.environ.get("CONDUCTOR_KEY"),
        }
    )

    print(f"🚀 DBOS ingestion worker started (PID {os.getpid()})")
    DBOS.launch()
    threading.Event().wait()
