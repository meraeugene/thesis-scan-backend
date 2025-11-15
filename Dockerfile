FROM python:3.10-slim

# Install system libraries needed by OpenCV + EasyOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first
COPY requirements.txt .

# Install Python packages without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose but do NOT set PORT
EXPOSE 8080

# Use $PORT from Railway runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
