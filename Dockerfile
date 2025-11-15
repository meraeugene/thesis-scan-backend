# Use Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy dependencies first (for caching)
COPY requirements.txt .
COPY .env .env

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
