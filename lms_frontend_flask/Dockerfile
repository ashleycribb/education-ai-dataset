# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app_frontend

# Copy the requirements file into the container at /app_frontend
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app_frontend
# This includes app.py, config.py, models.py, extensions.py, and static/ & templates/ folders
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV FLASK_APP app.py
ENV FLASK_ENV production
# Production Gunicorn settings
ENV PYTHONUNBUFFERED 1
# Note: SECRET_KEY and DATABASE_URL should be passed as environment variables during runtime, not baked here.

# Command to run the application using Gunicorn
# Ensure the 'app:app' part correctly points to the Flask app instance in app.py
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "app:app"]
