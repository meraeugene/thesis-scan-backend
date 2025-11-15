import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # fallback to 8000 if PORT not set
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
