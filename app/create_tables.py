# app/create_tables.py

from app.database import Base, engine
from app.models import Thesis, User, Bookmark, SearchHistory, Librarian

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
