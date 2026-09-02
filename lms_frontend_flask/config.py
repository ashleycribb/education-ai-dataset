import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
env_file_path = os.path.join(basedir, ".env")

if os.path.exists(env_file_path):
    load_dotenv(env_file_path)
    # print(f"INFO: Loaded .env file from {env_file_path}") # For debugging
else:
    print(f"INFO: .env file not found at {env_file_path}, using environment variables or defaults.")

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-for-lms' # Changed default slightly for uniqueness
    # Ensure the DATABASE_URL uses 'postgresql://' not 'postgresql+psycopg2://' for SQLAlchemy compatibility
    SQLALCHEMY_DATABASE_URI = os.environ.get('FLASK_DATABASE_URL') or \
                              'postgresql://lms_user:lms_password@localhost:5432/lms_db_test_default'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_SWATCH = 'cerulean' # Optional: For theming Flask-Admin

    # For debugging:
    # print(f"DEBUG: FLASK_SECRET_KEY: {SECRET_KEY}")
    # print(f"DEBUG: FLASK_DATABASE_URL (from env): {os.environ.get('FLASK_DATABASE_URL')}")
    # print(f"DEBUG: SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
