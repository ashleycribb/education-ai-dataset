# mcp_server_fastapi/app/config.py
import os
from starlette.config import Config
from starlette.datastructures import Secret

# Load .env file if it exists (for local development)
# Create a .env file in the mcp_server_fastapi directory (one level up from this app directory):
# Example .env content:
# DATABASE_URL="postgresql+asyncpg://mcp_user:mcp_password@localhost:5432/mcp_db_test"

# Get the directory of the current file (config.py which is in app/)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of app/ (which is mcp_server_fastapi/)
base_dir = os.path.dirname(current_file_dir)
env_file_path = os.path.join(base_dir, ".env")

# print(f"DEBUG: Attempting to load .env from: {env_file_path}") # For debugging path issues

try:
    if os.path.exists(env_file_path):
        config = Config(env_file_path)
        # print(f"DEBUG: Loaded .env file from {env_file_path}")
    else:
        # print(f"DEBUG: .env file not found at {env_file_path}. Using environment variables or defaults.")
        config = Config() # Load from environment if .env not found
except Exception as e:
    print(f"INFO: Error loading .env file from {env_file_path}, using environment variables or defaults. Error: {e}")
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret, default="postgresql+asyncpg://mcp_user:mcp_password@db:5432/mcp_db_default") # Default for Docker
# print(f"DEBUG: DATABASE_URL loaded as: {str(DATABASE_URL)}") # For debugging if needed by user
# Note: Changed default to 'db:5432' for typical Docker Compose service name. For local, .env should override.
