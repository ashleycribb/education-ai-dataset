# ai_assistant_service/db.py
from databases import Database
from .config import DATABASE_URL
# import os # Not strictly needed here but often useful

database = Database(str(DATABASE_URL))

async def connect_db():
    await database.connect()
    print("INFO:     Database connection established.") # Added for server log

async def disconnect_db():
    await database.disconnect()
    print("INFO:     Database connection closed.") # Added for server log

async def get_db() -> Database: # Added for potential direct use, e.g. in dependencies
    return database

async def create_raw_xapi_table_if_not_exists():
    # Note: CREATE EXTENSION ideally run once by a superuser.
    # Using uuid_generate_v4() from pgcrypto.

    # Attempt to create extension, fail gracefully if permissions are not enough
    # as it might already exist or be created by a DBA.
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

    # Ensure DB is connected before transaction
    # This check might be redundant if called after connect_db() in startup, but safe.
    was_connected_already = database.is_connected
    if not was_connected_already:
        await database.connect()
        print("INFO:     DB connection opened for table creation.")

    async with database.transaction(): # Use transaction for DDL block
        try:
            await database.execute(query=create_extension_query)
            print("INFO:     Ensured pgcrypto extension exists or attempted creation.")
        except Exception as e:
            # Log this warning, but don't let it stop table creation
            print(f"WARNING:  Could not ensure pgcrypto extension. uuid_generate_v4() might fail if not available. Error: {e}")

        await database.execute(query=create_table_query)
        print("INFO:     Ensured raw_xapi_statements table exists.")
        await database.execute(query=create_idx_actor_query)
        await database.execute(query=create_idx_verb_query)
        await database.execute(query=create_idx_activity_query)
        print("INFO:     Ensured indexes on raw_xapi_statements table exist.")

    if not was_connected_already: # Disconnect only if connected specifically for this function
        await database.disconnect()
        print("INFO:     DB connection closed after table creation.")
