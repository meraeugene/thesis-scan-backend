# backend/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv

# load_dotenv()  # loads .env into environment

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:qWxdxHPwqEEIBZckfQsWIdUaQKDseiaD@gondola.proxy.rlwy.net:13656/railway"

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
