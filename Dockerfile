# Dockerfile for MAS (code-refactor-mas)

# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command (can be overridden in docker-compose.yml)
CMD ["python", "updated_main_with_rich.py"]
