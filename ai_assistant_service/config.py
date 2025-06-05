# ai_assistant_service/config.py
import os
from starlette.config import Config
from starlette.datastructures import Secret

# Get the directory of the current file (config.py which is in app/ or ai_assistant_service/)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming .env file is in the same directory as this config.py for simplicity of service
env_file_path = os.path.join(current_file_dir, ".env")

# print(f"DEBUG: [config.py] Attempting to load .env from: {env_file_path}") # For debugging path issues

try:
    if os.path.exists(env_file_path):
        config = Config(env_file_path)
        # print(f"DEBUG: [config.py] Loaded .env file from {env_file_path}")
    else:
        # print(f"DEBUG: [config.py] .env file not found at {env_file_path}. Using environment variables or defaults.")
        config = Config() # Load from environment if .env not found
except Exception as e:
    print(f"Warning: Error initializing Config from {env_file_path if os.path.exists(env_file_path) else 'environment variables'}. Error: {e}")
    config = Config() # Fallback to environment variables or defaults

# Default for Docker, expecting .env to override for local or other deployments
DATABASE_URL = config("AIA_DATABASE_URL", cast=Secret, default="postgresql+asyncpg://aia_user:aia_password@db:5432/main_lms_db")
# print(f"DEBUG: [config.py] DATABASE_URL loaded as: {str(DATABASE_URL)}")

# Note for user:
# Ensure a .env file is created in the `ai_assistant_service` directory with the line:
# AIA_DATABASE_URL="postgresql+asyncpg://your_user:your_password@your_host:your_port/your_db"
# Example for local development:
# AIA_DATABASE_URL="postgresql+asyncpg://aia_user:aia_password@localhost:5432/main_lms_db_test_default"
# The default above assumes a Docker setup where 'db' is the service name for PostgreSQL.
# The database 'main_lms_db_test_default' or 'main_lms_db' should exist.
# The user 'aia_user' with 'aia_password' should have permissions on that database.
# The DDL for raw_xapi_statements table also needs to be applied to the database.
# The pgcrypto extension needs to be enabled in the PostgreSQL database (CREATE EXTENSION IF NOT EXISTS "pgcrypto";) by a superuser.
