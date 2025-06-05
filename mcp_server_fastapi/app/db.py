from databases import Database
from .config import DATABASE_URL

# Global database instance
# The actual connection is managed by startup/shutdown events in main.py
database = Database(str(DATABASE_URL))

async def connect_db():
    """Connects to the database."""
    await database.connect()
    # You might want to add a log message here in a real application
    # print("Database connection established.")

async def disconnect_db():
    """Disconnects from the database."""
    await database.disconnect()
    # print("Database connection closed.")

# The fake_context_db is no longer needed as we are moving to a real database.
# If you need to execute a simple query to ensure the table exists or create it,
# you could add a function here, e.g., to be called during startup.
# For example:
# async def create_mcp_contexts_table_if_not_exists():
#     query = """
#     CREATE TABLE IF NOT EXISTS mcp_contexts (
#         context_id TEXT PRIMARY KEY,
#         model_id TEXT,
#         user_id TEXT,
#         context_payload JSONB NOT NULL,
#         last_updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
#     );
#     """
#     await database.execute(query=query)
#     # print("Checked/created mcp_contexts table.")
# This function could then be called in main.py's startup event after connect_db.
# However, proper migrations (e.g., with Alembic) are recommended for production.
# For this task, we assume the table is created manually or by another process.
