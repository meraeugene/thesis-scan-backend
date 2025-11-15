# 1) Use lightweight Python base image
FROM python:3.10-slim

# 2) Set working directory
WORKDIR /app

# 3) Install minimal system dependencies required by OpenCV + psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

# 4) Copy requirements.txt
COPY requirements.txt .

# 5) Install everything without cache (keeps image small)
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy the entire app
COPY . .

# 7) Expose port 8000 (Railway uses this)
EXPOSE 8000

# 8) Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
