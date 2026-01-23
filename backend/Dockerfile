# Use specific stable version (Debian 12 Bookworm) to ensure package availability
FROM python:3.10-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
# libgl1: Replacement for libgl1-mesa-glx in newer Debian versions
# libglib2.0-0: Required for Glib
# libsm6, libxext6, libxrender1: Required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
