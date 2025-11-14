
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime
# Librarian CRUD
def get_librarian(db: Session, username: str):
    return db.query(models.Librarian).filter(models.Librarian.username == username).first()

def get_librarian_by_id(db: Session, librarian_id: int):
    return db.query(models.Librarian).filter(models.Librarian.id == librarian_id).first()

def create_librarian(db: Session, librarian: schemas.LibrarianCreate):
    db_librarian = models.Librarian(**librarian.dict())
    db.add(db_librarian)
    db.commit()
    db.refresh(db_librarian)
    return db_librarian

def get_user(db: Session, student_id: str):
    return db.query(models.User).filter(models.User.student_id == student_id).first()

def get_user_by_id(db: Session, id: str):
    return db.query(models.User).filter(models.User.id == id).first()

# Bookmark CRUD
def add_bookmark(db: Session, bookmark: schemas.BookmarkCreate):
    db_bookmark = models.Bookmark(**bookmark.dict())
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

def get_bookmarks(db: Session, student_id: str):
    return db.query(models.Bookmark).filter(models.Bookmark.student_id == student_id).all()

# Get a specific bookmark
def get_bookmark(db: Session, student_id: str, thesis_id: int):
    return (
        db.query(models.Bookmark)
        .filter(
            models.Bookmark.student_id == student_id,
            models.Bookmark.thesis_id == thesis_id
        )
        .first()
    )

# Delete a bookmark
def delete_bookmark(db: Session, bookmark: models.Bookmark):
    db.delete(bookmark)
    db.commit()
    return True


# SearchHistory CRUD
def add_search_history(db: Session, history: schemas.SearchHistoryCreate):
    data = history.dict()
    data['access_location'] = 'Off-Campus'
    # Use current timestamp for date_accessed
    data['date_accessed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db_history = models.SearchHistory(**data)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_search_history(db: Session, student_id: str):
    return db.query(models.SearchHistory).filter(models.SearchHistory.student_id == student_id).all()

def create_user(db: Session, user: schemas.UserCreate):
    user_data = user.dict()
    user_data['date_registered'] = datetime.now().strftime('%Y-%m-%d')
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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
    return db.query(models.Thesis).filter(models.Thesis.id == thesis_id).first()

def get_theses(db: Session):
    return db.query(models.Thesis).all()

def delete_thesis(db: Session, thesis_id: int):
    thesis = db.query(models.Thesis).filter(models.Thesis.id == thesis_id).first()
    if thesis:
        # Delete related bookmarks and search history
        db.query(models.Bookmark).filter(models.Bookmark.thesis_id == thesis_id).delete()
        db.query(models.SearchHistory).filter(models.SearchHistory.thesis_id == thesis_id).delete()
        # Delete the thesis
        db.delete(thesis)
        db.commit()
        return True
    return False

def get_users(db: Session):
    return db.query(models.User).all()

def delete_user(db: Session, user):
    db.delete(user)
    db.commit()
