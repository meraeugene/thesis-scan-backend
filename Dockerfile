FROM python:3.10-slim

# Install required libs for OpenCV + EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements separately so Docker can cache layers
COPY requirements.txt .

# Install Python dependencies (CPU-only PyTorch!)
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI project
COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
