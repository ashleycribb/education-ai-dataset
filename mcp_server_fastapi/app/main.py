from fastapi import FastAPI, HTTPException, Body, status, Depends
from typing import Dict, Any, Optional
from pydantic import ValidationError # Import for handling Pydantic errors
from datetime import datetime


from . import crud
from . import models

app = FastAPI(title="MCP Server", version="0.1.0")

@app.get("/")
async def read_root():
    return {"message": "MCP Server is running"}

@app.put("/contexts/{context_id}", response_model=models.ContextData, status_code=status.HTTP_200_OK)
async def update_context_endpoint(
    context_id: str, 
    payload: Dict[str, Any] = Body(...)
):
    """
    Create or update a context.
    - **contextId**: The ID of the context to create or update.
    - **modelId**: Identifier for the model associated with this context.
    - **userId**: Identifier for the user associated with this context.
    - **contextData**: The actual payload for the context.
    - **lastUpdated** (optional): Will be overridden by the server.
    """
    try:
        # Prepare data for Pydantic model, ensuring aliases are handled if necessary
        # Pydantic's allow_population_by_field_name = True and by_alias = True in Config
        # should handle this, but we can be explicit.
        
        # We use the context_id from the path as authoritative
        model_data = {
            "contextId": context_id, # from path
            "modelId": payload.get("modelId"),
            "userId": payload.get("userId"),
            "contextData": payload.get("contextData", {}), # Default to empty dict if not provided
            # lastUpdated will be set by the model's default_factory or crud function
        }
        
        # Validate and create the Pydantic model instance
        # This will use field names if aliases are not present in model_data keys
        # thanks to allow_population_by_field_name = True
        context_to_create = models.ContextData(**model_data)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors(),
        )
    except Exception as e: # Catch any other unexpected error during model creation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing request payload: {str(e)}"
        )

    updated_context = crud.create_or_update_context(context_id=context_id, context_in=context_to_create)
    return updated_context

@app.get("/contexts/{context_id}", response_model=models.ContextData)
async def get_context_endpoint(context_id: str):
    """
    Retrieve a context by its ID.
    """
    db_context = crud.get_context(context_id=context_id)
    if db_context is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")
    return db_context

@app.delete("/contexts/{context_id}", response_model=models.ContextData)
async def delete_context_endpoint(context_id: str):
    """
    Delete a context by its ID.
    """
    deleted_context = crud.delete_context(context_id=context_id)
    if deleted_context is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")
    return deleted_context

# To run this app (from the mcp_server_fastapi directory):
# uvicorn app.main:app --reload
#
# Example PUT request body for /contexts/test_context_123:
# {
#     "modelId": "model_xyz_1.0",
#     "userId": "user_abc_789",
#     "contextData": {
#         "settingA": "valueA",
#         "settingB": 123,
#         "nested": {"key": "value"}
#     }
# }
# Note: "contextId" and "lastUpdated" are handled by the server/model.
# Pydantic model uses aliases, so "modelId" in payload maps to "model_id" in Python.
# The response will show "contextId", "modelId", "userId", "contextData", "lastUpdated".

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
