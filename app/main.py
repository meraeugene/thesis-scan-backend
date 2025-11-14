
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.routers import users, theses, auth, reports, ocr
from app.config import STATIC_DIR

# Create app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://thesis-scan.vercel.app/"],  # Allow all origins for development
    # allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print(f"Warning: Static directory {STATIC_DIR} does not exist.")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(theses.router)
app.include_router(reports.router)
app.include_router(ocr.router)