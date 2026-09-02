# ai_assistant_service/db.py
from databases import Database
from .config import DATABASE_URL
# import os # Not strictly needed here but often useful

database = Database(str(DATABASE_URL))

async def connect_db():
    await database.connect()
    print("INFO:     Database connection established for AI Assistant Service.") # Added for server log

async def disconnect_db():
    await database.disconnect()
    print("INFO:     Database connection closed for AI Assistant Service.") # Added for server log

async def get_db() -> Database: # Added for potential direct use
    return database

async def create_raw_xapi_table_if_not_exists():
    # Note: CREATE EXTENSION ideally run once by a superuser.
    # Using uuid_generate_v4() from pgcrypto.

    create_extension_query = """CREATE EXTENSION IF NOT EXISTS "pgcrypto";"""

    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_xapi_statements (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        statement JSONB NOT NULL,
        received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        actor_mbox TEXT,
        verb_id TEXT,
        activity_id TEXT
    );"""

    create_idx_actor_query = "CREATE INDEX IF NOT EXISTS idx_raw_xapi_actor_mbox ON raw_xapi_statements (actor_mbox);"
    create_idx_verb_query = "CREATE INDEX IF NOT EXISTS idx_raw_xapi_verb_id ON raw_xapi_statements (verb_id);"
    create_idx_activity_query = "CREATE INDEX IF NOT EXISTS idx_raw_xapi_activity_id ON raw_xapi_statements (activity_id);"

    was_connected_already = database.is_connected
    if not was_connected_already:
        await database.connect()
        print("INFO:     DB connection temporarily opened for table creation (AI Assistant Service).")

    async with database.transaction():
        try:
            await database.execute(query=create_extension_query)
            print("INFO:     Ensured pgcrypto extension exists or attempted creation (AI Assistant Service).")
        except Exception as e:
            print(f"WARNING:  Could not ensure pgcrypto extension. uuid_generate_v4() might fail if not available. Error: {e} (AI Assistant Service)")

        await database.execute(query=create_table_query)
        print("INFO:     Ensured raw_xapi_statements table exists (AI Assistant Service).")
        await database.execute(query=create_idx_actor_query)
        await database.execute(query=create_idx_verb_query)
        await database.execute(query=create_idx_activity_query)
        print("INFO:     Ensured indexes on raw_xapi_statements table exist (AI Assistant Service).")

    if not was_connected_already:
        await database.disconnect()
        print("INFO:     DB connection closed after table creation (AI Assistant Service).")
