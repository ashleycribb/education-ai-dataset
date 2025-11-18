# 1. Base Image
FROM python:3.9-slim

# 2. Set Working Directory
WORKDIR /app

# 3. Install System Dependencies (if any, e.g., for specific ML model backends)
# RUN apt-get update && apt-get install -y --no-install-recommends some-system-lib && rm -rf /var/lib/apt/lists/*

# 4. Copy and Install Python Requirements
# For a real build, use a requirements.txt file:
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# For this prototype, install directly.
# Using CPU-only PyTorch for simpler Docker builds. For GPU, refer to NVIDIA CUDA base images.
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    torch --index-url https://download.pytorch.org/whl/cpu \
    transformers \
    pydantic \
    sentencepiece \
    accelerate \
    peft

# 5. Copy Application Code
# Assuming all necessary Python files are in the root of the build context
COPY aita_interaction_service.py .
COPY moderation_service.py .
COPY model_loader_utils.py . # Added model_loader_utils.py

# Ensure the k12_mcp_client_sdk is available for import
# If it's a local directory SDK:
COPY k12_mcp_client_sdk/ k12_mcp_client_sdk/
# Add current directory to PYTHONPATH to allow imports from k12_mcp_client_sdk and model_loader_utils from root
ENV PYTHONPATH "${PYTHONPATH}:/app"


# 6. Create Placeholder Adapter Directories (as defined in ADAPTER_CONFIG)
# These are created so the os.path.exists() checks in the service don't immediately fail
# if actual adapter files are not mounted or copied.
RUN mkdir -p /app/adapters/reading_explorer_pilot1
RUN mkdir -p /app/adapters/eco_explorer_pilot1
# Add more RUN mkdir -p for other adapter paths defined in ADAPTER_CONFIG

# 7. Expose Port
EXPOSE 8000

# 8. Command to Run Application
# The service script (aita_interaction_service.py) calls uvicorn.run() itself.
CMD ["python", "aita_interaction_service.py"]
