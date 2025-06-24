# ai_assistant_service/config.py
import os
from starlette.config import Config
from starlette.datastructures import Secret

current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_dir, ".env")

try:
    if os.path.exists(env_file_path):
        config = Config(env_file_path)
        # print(f"DEBUG: [config.py] Loaded .env file from {env_file_path}")
    else:
        # print(f"DEBUG: [config.py] .env file not found at {env_file_path}. Using environment variables or defaults.")
        config = Config() # Will load from environment or use defaults
except Exception as e:
    print(f"Warning: Error initializing Config from {env_file_path if os.path.exists(env_file_path) else 'environment variables'}. Error: {e}")
    config = Config() # Fallback to environment variables or defaults

DATABASE_URL = config("AIA_DATABASE_URL", cast=Secret, default="postgresql+asyncpg://aia_user:aia_password@localhost:5432/main_lms_db_test_default")

# Note for user:
# Ensure a .env file is created in the `ai_assistant_service` directory with the line:
# AIA_DATABASE_URL="postgresql+asyncpg://your_user:your_password@your_host:your_port/your_db"
# Example for local development:
# AIA_DATABASE_URL="postgresql+asyncpg://aia_user:aia_password@localhost:5432/main_lms_db_test_default"
# The default above uses 'localhost'. For Docker, you might use a service name like 'db'.
# The database 'main_lms_db_test_default' or your specified DB should exist.
# The user 'aia_user' with 'aia_password' should have permissions on that database.
# The pgcrypto extension needs to be enabled in the PostgreSQL database (CREATE EXTENSION IF NOT EXISTS "pgcrypto";) by a superuser.
