FROM python:3.10-slim

# Install system libs for OpenCV/EasyOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python packages without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port 8080
EXPOSE 8080

# Run Python directly (reads PORT from environment)
CMD ["python", "app/main.py"]
