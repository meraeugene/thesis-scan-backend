# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.types import Date
from app.database import Base

class Thesis(Base):
  __tablename__ = "theses"
  id = Column(Integer, primary_key=True, index=True)
  title = Column(String, nullable=False)
  authors = Column(String, nullable=False)
  program_course = Column(String, nullable=False)
  date_published = Column(Date, nullable=False)
  edition_version = Column(String, nullable=True)
  abstract = Column(Text, nullable=True)
  keywords = Column(String, nullable=True)
  date_uploaded = Column(String, nullable=False)


class User(Base):
  __tablename__ = "users"
  id = Column(Integer, primary_key=True, index=True)
  full_name = Column(String, nullable=False)
  program_course = Column(String, nullable=False)
  student_id = Column(String, unique=True, index=True, nullable=False)
  year_level = Column(String, nullable=False)
  email = Column(String, unique=True, index=True, nullable=False)
  password = Column(String, nullable=False)
  profile_picture = Column(String, nullable=True)
  date_registered = Column(String, nullable=False)
  last_login = Column(String, nullable=True)  # Stores the last login timestamp

# Bookmark model
class Bookmark(Base):
  __tablename__ = "bookmarks"
  id = Column(Integer, primary_key=True, index=True)
  student_id = Column(String, nullable=False)
  thesis_id = Column(Integer, nullable=False)
  thesis_title = Column(String, nullable=False)
  author = Column(String, nullable=False)
  program = Column(String, nullable=False)
  date_bookmarked = Column(String, nullable=False)

# SearchHistory model
class SearchHistory(Base):
  __tablename__ = "search_history"
  id = Column(Integer, primary_key=True, index=True)
  student_id = Column(String, nullable=False)
  thesis_id = Column(Integer, nullable=False)
  book_title = Column(String, nullable=False)
  author = Column(String, nullable=False)
  date_accessed = Column(String, nullable=False)
  access_location = Column(String, nullable=False)

# Librarian model
class Librarian(Base):
  __tablename__ = "librarians"
  id = Column(Integer, primary_key=True, index=True)
  full_name = Column(String, nullable=False)
  email = Column(String, unique=True, index=True, nullable=False)
  username = Column(String, unique=True, index=True, nullable=False)
  role = Column(String, nullable=False)
  contact = Column(String, nullable=True)
  password = Column(String, nullable=False)
  profile_picture = Column(String, nullable=True)
