from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime
from sqlalchemy import func

# ---------------------------
# Librarian CRUD
# ---------------------------
def get_all_librarians(db: Session):
    return db.query(models.Librarian).all()

def get_librarians(db: Session):
    return db.query(models.Librarian).all()

def get_librarian(db: Session, username: str):
    return db.query(models.Librarian).filter(models.Librarian.username == username).first()

def get_librarian_by_username(db: Session, username: str):
    return db.query(models.Librarian).filter(models.Librarian.username == username).first()

def get_librarian_by_id(db: Session, librarian_id: int):
    return db.query(models.Librarian).filter(models.Librarian.id == librarian_id).first()

def create_librarian(db: Session, librarian: schemas.LibrarianCreate):
    db_librarian = models.Librarian(**librarian.dict())
    db.add(db_librarian)
    db.commit()
    db.refresh(db_librarian)
    return db_librarian

# ---------------------------
# User CRUD
# ---------------------------
def get_user(db: Session, student_id: str):
    return db.query(models.User).filter(models.User.student_id == student_id).first()

def get_user_by_id(db: Session, id: str):
    return db.query(models.User).filter(models.User.id == id).first()

def create_user(db: Session, user: schemas.UserCreate):
    user_data = user.dict()
    user_data['date_registered'] = datetime.now().strftime('%Y-%m-%d')
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.query(models.User).all()

def delete_user(db: Session, user):
    db.delete(user)
    db.commit()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def update_user_password(db: Session, user, new_password: str):
    # If storing plaintext passwords (not recommended)
    user.password = new_password
    # To hash passwords (recommended), uncomment below:
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # user.password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(user)
    return user

# ---------------------------
# Bookmark CRUD
# ---------------------------
def add_bookmark(db: Session, bookmark: schemas.BookmarkCreate):
    db_bookmark = models.Bookmark(**bookmark.dict())
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

def get_bookmarks(db: Session, student_id: str):
    return db.query(models.Bookmark).filter(models.Bookmark.student_id == student_id).all()

def get_bookmark(db: Session, student_id: str, thesis_id: int):
    return db.query(models.Bookmark).filter(
        models.Bookmark.student_id == student_id,
        models.Bookmark.thesis_id == thesis_id
    ).first()

def delete_bookmark(db: Session, bookmark: models.Bookmark):
    db.delete(bookmark)
    db.commit()
    return True

# ---------------------------
# Search History CRUD
# ---------------------------
def add_search_history(db: Session, history: schemas.SearchHistoryCreate):
    data = history.dict()
    data['access_location'] = 'Off-Campus'
    data['date_accessed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_history = models.SearchHistory(**data)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_search_history(db: Session, student_id: str):
    return db.query(models.SearchHistory).filter(models.SearchHistory.student_id == student_id).all()

# ---------------------------
# Thesis CRUD
# ---------------------------
def create_thesis(db: Session, thesis: schemas.ThesisCreate):
    thesis_data = thesis.dict()
    if not thesis_data.get('date_uploaded'):
        thesis_data['date_uploaded'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_thesis = models.Thesis(**thesis_data)
    db.add(db_thesis)
    db.commit()
    db.refresh(db_thesis)
    return db_thesis

def get_thesis(db: Session, thesis_id: int):
    return db.query(models.Thesis).filter(
        models.Thesis.id == thesis_id,
        models.Thesis.is_deleted == False
    ).first()

def get_theses_with_views(db: Session):
    """
    Returns all theses along with their view count (based on SearchHistory).
    """
    results = (
        db.query(
            models.Thesis,
            func.count(models.SearchHistory.id).label("views")
        )
        .outerjoin(models.SearchHistory, models.Thesis.id == models.SearchHistory.thesis_id)
        .filter(models.Thesis.is_deleted == False)
        .group_by(models.Thesis.id)
        .all()
    )

    return [
        schemas.ThesisWithViews(
            id=thesis.id,
            title=thesis.title,
            authors=thesis.authors,
            program_course=thesis.program_course,
            date_published=thesis.date_published,
            edition_version=thesis.edition_version,
            abstract=thesis.abstract,
            keywords=thesis.keywords,
            date_uploaded=thesis.date_uploaded,
            views=views
        )
        for thesis, views in results
    ]

def get_theses(db: Session):
    return db.query(models.Thesis).filter(models.Thesis.is_deleted == False).all()

def get_deleted_theses(db: Session):
    return db.query(models.Thesis).filter(models.Thesis.is_deleted == True).all()

def delete_thesis(db: Session, thesis_id: int):
    thesis = db.query(models.Thesis).filter(models.Thesis.id == thesis_id).first()
    if thesis:
        thesis.is_deleted = True
        db.commit()
        return True
    return False

def restore_thesis(db: Session, thesis_id: int):
    thesis = db.query(models.Thesis).filter(
        models.Thesis.id == thesis_id,
        models.Thesis.is_deleted == True
    ).first()
    if thesis:
        thesis.is_deleted = False
        thesis.date_restored = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db.commit()
        db.refresh(thesis)
        return thesis
    return None
