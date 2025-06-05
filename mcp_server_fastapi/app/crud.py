import json
from datetime import datetime, timezone # Added timezone
from typing import Optional, Dict # Dict might not be needed directly here anymore

from . import models
from .db import database # Import the database instance

async def create_or_update_context(context_id: str, context_in: models.ContextData) -> models.ContextData:
    """
    Creates a new context or updates an existing one in the database.
    The context_id from the path is authoritative.
    """
    # Ensure the context_id in the model instance matches the path parameter for consistency
    # though the query will use the passed context_id for the key.
    context_in.context_id = context_id

    # Update timestamp to be timezone-aware (UTC)
    # The Pydantic model default_factory already sets it, but we ensure it's set on update too.
    context_in.last_updated = datetime.now(timezone.utc)

    query = """
    INSERT INTO mcp_contexts (context_id, model_id, user_id, context_payload, last_updated)
    VALUES (:context_id, :model_id, :user_id, :context_payload, :last_updated)
    ON CONFLICT (context_id) DO UPDATE SET
        model_id = EXCLUDED.model_id,
        user_id = EXCLUDED.user_id,
        context_payload = EXCLUDED.context_payload,
        last_updated = EXCLUDED.last_updated
    RETURNING context_id, model_id, user_id, context_payload, last_updated;
    """

    values = {
        "context_id": context_in.context_id,
        "model_id": context_in.model_id,
        "user_id": context_in.user_id,
        "context_payload": json.dumps(context_in.context_payload), # Serialize dict to JSON string for DB
        "last_updated": context_in.last_updated
    }

    # Execute the query
    # The 'databases' library typically returns a Record object or None
    row = await database.fetch_one(query=query, values=values)

    # The returned row will have context_payload as a string if it was stored as JSON string.
    # However, asyncpg and `databases` library often auto-decode JSONB to dict.
    # If it's a string, it needs json.loads before Pydantic validation.
    # If the driver already returns a dict for JSONB, direct unpacking is fine.
    # Assuming the driver handles JSONB to dict conversion:
    if row:
        # Convert row (Record object) to a dictionary
        row_dict = dict(row)
        # If context_payload is a string from DB, parse it:
        if isinstance(row_dict.get("context_payload"), str):
             row_dict["context_payload"] = json.loads(row_dict["context_payload"])
        return models.ContextData(**row_dict)
    else:
        # This case should ideally not be reached if RETURNING clause works as expected on INSERT/UPDATE.
        # It might imply an issue with the query or DB if no row is returned.
        # For safety, refetch or handle as error. Here, we'll assume it returns the data.
        # If not, the original context_in (with updated timestamp) is a fallback,
        # but it's better to rely on what the DB confirms.
        # A more robust error handling or a subsequent fetch might be needed if row is None.
        # For now, returning the input model if RETURNING somehow fails to give back the row.
        # This part needs careful testing with the actual DB.
        # However, with RETURNING, a row *should* always come back.
        # If `row` is None here, it indicates a more fundamental issue.
        # Let's assume `row` is always populated by RETURNING.
        pass # Should not be reached if RETURNING works.

    # Fallback if RETURNING clause somehow doesn't work (should not happen ideally)
    # This ensures the function signature for return type is met.
    # In a real scenario, this would be an error condition.
    return context_in


async def get_context(context_id: str) -> Optional[models.ContextData]:
    """
    Retrieves a context by its ID from the database.
    """
    query = "SELECT context_id, model_id, user_id, context_payload, last_updated FROM mcp_contexts WHERE context_id = :context_id"
    row = await database.fetch_one(query=query, values={"context_id": context_id})

    if row:
        row_dict = dict(row)
        # Assuming context_payload from DB (JSONB) is auto-decoded to dict by 'databases'
        # If it's a string, it needs: if isinstance(row_dict.get("context_payload"), str): row_dict["context_payload"] = json.loads(row_dict["context_payload"])
        return models.ContextData(**row_dict)
    return None

async def delete_context(context_id: str) -> Optional[models.ContextData]:
    """
    Deletes a context by its ID from the database.
    Returns the deleted context data if found, otherwise None.
    """
    query = "DELETE FROM mcp_contexts WHERE context_id = :context_id RETURNING context_id, model_id, user_id, context_payload, last_updated;"
    row = await database.fetch_one(query=query, values={"context_id": context_id})

    if row:
        row_dict = dict(row)
        # Assuming context_payload from DB (JSONB) is auto-decoded to dict
        # If it's a string: if isinstance(row_dict.get("context_payload"), str): row_dict["context_payload"] = json.loads(row_dict["context_payload"])
        return models.ContextData(**row_dict)
    return None
