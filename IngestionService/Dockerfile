FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements (create requirements.txt if not present)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "ingestion_service:app", "--host", "0.0.0.0", "--port", "8000"]