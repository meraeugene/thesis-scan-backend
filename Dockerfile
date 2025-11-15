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

# Copy app
COPY . .

# Railway provides $PORT at runtime
ENV PORT=8080

EXPOSE 8080

# Use sh -c so $PORT becomes a valid integer at runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
