from google.cloud import datastore
from app.core.config import settings
from typing import Optional

_db_client: Optional[datastore.Client] = None

def get_firestore_client() -> datastore.Client:
    """Get Datastore client singleton."""
    global _db_client
    if _db_client is None:
        if settings.GCP_PROJECT_ID:
            _db_client = datastore.Client(project=settings.GCP_PROJECT_ID)
        else:
            # Use default project from environment
            _db_client = datastore.Client()
    return _db_client

def get_db():
    """Dependency for Datastore database."""
    return get_firestore_client()
