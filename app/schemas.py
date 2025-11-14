from pydantic import BaseModel
from datetime import date
# Librarian schema
class LibrarianCreate(BaseModel):
    full_name: str
    email: str
    username: str
    role: str
    contact: str | None = None
    password: str
    profile_picture: str | None = None

class LibrarianOut(BaseModel):
    id: int
    full_name: str
    email: str
    username: str
    role: str
    contact: str | None = None
    profile_picture: str | None = None

    class Config:
        from_attributes = True

class ThesisCreate(BaseModel):
    title: str
    authors: str
    program_course: str
    date_published: date
    edition_version: str | None = None
    abstract: str | None = None
    keywords: str | None = None
    date_uploaded: str | None = None  # Will be set automatically if not provided

class ThesisOut(ThesisCreate):
    id: int

    class Config:
        from_attributes = True  # For Pydantic v2

class UserCreate(BaseModel):
    full_name: str
    program_course: str
    student_id: str
    year_level: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    program_course: str
    student_id: str
    year_level: str
    email: str
    profile_picture: str | None = None
    last_login: str | None = None

    class Config:
        from_attributes = True  # For Pydantic v2

# Bookmark schema
class BookmarkCreate(BaseModel):
    student_id: str
    thesis_id: int
    thesis_title: str
    author: str
    program: str
    date_bookmarked: str

class BookmarkOut(BookmarkCreate):
    id: int

    class Config:
        from_attributes = True

# SearchHistory schema
class SearchHistoryCreate(BaseModel):
    student_id: str
    thesis_id: int
    book_title: str
    author: str
    date_accessed: str
    access_location: str

class SearchHistoryOut(SearchHistoryCreate):
    id: int

    class Config:
        from_attributes = True