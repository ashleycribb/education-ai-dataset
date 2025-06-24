from fastapi import FastAPI, HTTPException, Body, status
from typing import Dict, Any, Optional
from pydantic import ValidationError
from datetime import datetime

from . import crud
from . import models
from .db import connect_db, disconnect_db, create_mcp_contexts_table_if_not_exists # Import new function
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MCP Server", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup(): # Renamed for clarity, though 'startup' is fine
    await connect_db()
    await create_mcp_contexts_table_if_not_exists() # Add this call

@app.on_event("shutdown")
async def shutdown(): # Renamed for clarity, though 'shutdown' is fine
    await disconnect_db()

@app.get("/")
async def read_root():
    return {"message": "MCP Server is running"}

@app.put("/contexts/{context_id}", response_model=models.ContextData, status_code=status.HTTP_200_OK)
async def update_context_endpoint( # Made async
    context_id: str,
    payload: Dict[str, Any] = Body(...)
):
    try:
        # model_data uses aliases as keys, which Pydantic handles due to Config.validate_by_name = True
        model_data = {
            "contextId": context_id,
            "modelId": payload.get("modelId"),
            "userId": payload.get("userId"),
            "contextData": payload.get("contextData", {}),
            # lastUpdated is handled by Pydantic model default_factory or by CRUD on update
        }
        context_to_create = models.ContextData(**model_data)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing request payload: {str(e)}"
        )

    # Call the async crud function
    updated_context = await crud.create_or_update_context(context_id=context_id, context_in=context_to_create)
    return updated_context

@app.get("/contexts/{context_id}", response_model=models.ContextData)
async def get_context_endpoint(context_id: str): # Made async
    db_context = await crud.get_context(context_id=context_id) # Await async crud function
    if db_context is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")
    return db_context

@app.delete("/contexts/{context_id}", response_model=models.ContextData)
async def delete_context_endpoint(context_id: str): # Made async
    deleted_context = await crud.delete_context(context_id=context_id) # Await async crud function
    if deleted_context is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")
    return deleted_context

# To run this app (from the mcp_server_fastapi directory, one level up from 'app'):
# uvicorn app.main:app --reload --port 8001
#
# Example .env file in mcp_server_fastapi directory:
# DATABASE_URL="postgresql+asyncpg://mcp_user:mcp_password@localhost:5432/mcp_db_test"


if __name__ == "__main__":
    import uvicorn
    # Note: It's generally better to run uvicorn from the command line as specified above
    # especially when dealing with packages and ensuring the correct working directory.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True) # Pass app string for uvicorn.run
