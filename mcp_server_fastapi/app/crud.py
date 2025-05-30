from datetime import datetime
from typing import Optional, Dict

from . import models
from .db import fake_context_db

def create_or_update_context(context_id: str, context_in: models.ContextData) -> models.ContextData:
    """
    Creates a new context or updates an existing one in the fake_context_db.
    The context_id from the path is authoritative.
    """
    # Ensure the context_id in the model matches the path parameter
    if context_in.context_id != context_id:
        # Or handle this as an error, depending on desired behavior
        context_in.context_id = context_id
        
    context_in.last_updated = datetime.utcnow()
    fake_context_db[context_id] = context_in
    return context_in

def get_context(context_id: str) -> Optional[models.ContextData]:
    """
    Retrieves a context by its ID from the fake_context_db.
    """
    return fake_context_db.get(context_id)

def delete_context(context_id: str) -> Optional[models.ContextData]:
    """
    Deletes a context by its ID from the fake_context_db.
    Returns the deleted context data if found, otherwise None.
    """
    if context_id in fake_context_db:
        return fake_context_db.pop(context_id)
    return None
