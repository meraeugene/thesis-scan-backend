# 1️⃣ Use slim Python base image
FROM python:3.10-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Install system dependencies (small, needed for psycopg2, OpenCV)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        && rm -rf /var/lib/apt/lists/*

# 4️⃣ Copy requirements.txt
COPY requirements.txt .

# 5️⃣ Install Python dependencies with no cache
RUN python -m pip install --no-cache-dir -r requirements.txt

# 6️⃣ Copy app source code
COPY . .

# 7️⃣ Set FastAPI entry point
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
