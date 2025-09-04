FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PyTorch and gRPC
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose gRPC port
EXPOSE 50051

CMD ["python", "inference_service.py"]