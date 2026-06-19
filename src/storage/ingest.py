# src/storage/ingest.py

import os
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from franz.openrdf.connect import ag_connect
from franz.openrdf.rio.rdfformat import RDFFormat

# Automatically locate the .env file in parent directories and load its variables
load_dotenv(find_dotenv())

# --- Server Configuration Constants ---
AG_BASE_URL = os.getenv("AG_BASE_URL")
AG_REPO = os.getenv("AG_REPO")
AG_USER = os.getenv("AG_USER")
AG_PASSWORD = os.getenv("AG_PASSWORD")

def ingest_rdf_file(file_path: str, source_id: str, context_uri: Optional[str] = None) -> bool:
    """
    Ingests an N-Triples (.nt) file directly into the AllegroGraph repository.
    """
    # 1. Validate File Existence
    if not os.path.exists(file_path):
        print(f"[INGEST] ERROR: File not found at {file_path}")
        return False
        
    print(f"[INGEST] Connecting to AllegroGraph at {AG_BASE_URL}...")

    try:
        # 2. Connect directly to the Server and Repository
        conn = ag_connect(
            repo=AG_REPO,
            host=AG_BASE_URL,
            port=443, # Default secure port for AllegroGraph
            protocol='https', # Force connection to use secure HTTPS protocol
            user=AG_USER,
            password=AG_PASSWORD,
            create=True # Creates the repository automatically if it doesn't exist yet
        )
        
        print(f"[INGEST] Connection established. Uploading file: {file_path}")
        
        # 3. Ingest nt file using addFile
        conn.addFile(file_path, base=None, format=RDFFormat.NTRIPLES, context=context_uri)
        total_triples = conn.size()
        print(f"[INGEST] SUCCESS: File loaded. Repository '{AG_REPO}' now contains {total_triples} triples.")
        
        return True

    except Exception as e:
        print(f"[INGEST] FAILURE: Data loading failed. Error: {e}")
        return False
        
    finally:
        # 4. Ensure connection is closed
        if 'conn' in locals() and conn:
            conn.close()
            # print("[INGEST] Connection closed.")