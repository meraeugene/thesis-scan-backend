# Step 1: Use a lightweight Python image
FROM python:3.13-slim

# Step 2: Set working directory inside the container
WORKDIR /app

# Step 3: Copy requirements first to use Docker cache
COPY requirements.txt .

# Step 4: Install dependencies without pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your app code
COPY . .

# Step 6: Set the command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
