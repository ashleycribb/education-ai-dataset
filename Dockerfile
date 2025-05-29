# 1. Base Image
FROM python:3.9-slim

# 2. Set Working Directory
WORKDIR /app

# 3. Copy and Install Requirements
# Conceptual requirements.txt content:
# fastapi
# uvicorn[standard] # For ASGI server
# torch
# torchvision
# torchaudio
# transformers
# pydantic
# sentencepiece # Often a dependency for tokenizers
# accelerate # Often useful for transformers, though not strictly needed for this simple service yet

# For a real build, you'd have a requirements.txt file:
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# For this prototype, install directly.
# Note: Installing torch with CUDA support in Docker can be complex and requires nvidia-docker.
# This Dockerfile assumes CPU or a base torch installation. For GPU, specific torch versions
# and base images (e.g., nvidia/cuda) are needed.
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    torch --index-url https://download.pytorch.org/whl/cpu \
    transformers \
    pydantic \
    sentencepiece \
    accelerate

# 4. Copy Application Code
COPY aita_interaction_service.py .
# If you had other modules like a local moderation_service.py, copy them too:
# COPY moderation_service.py . 

# 5. Expose Port
EXPOSE 8000

# 6. Command to Run Application
# This will run the FastAPI app using Uvicorn.
# The service script itself has `uvicorn.run(app, host="0.0.0.0", port=8000)`
# so just running the python script is enough.
CMD ["python", "aita_interaction_service.py"]

# Alternatively, you can run uvicorn directly if the script doesn't call uvicorn.run():
# CMD ["uvicorn", "aita_interaction_service:app", "--host", "0.0.0.0", "--port", "8000"]
