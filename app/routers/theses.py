from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, database

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------
# Theses Routes
# -------------------

# 1. List all theses (active)
@router.get("/theses", response_model=list[schemas.ThesisOut])
def list_theses(db: Session = Depends(get_db)):
    return crud.get_theses(db)

# 2. List deleted theses
@router.get("/theses/deleted", response_model=list[schemas.ThesisOut])
def list_deleted_theses(db: Session = Depends(get_db)):
    return crud.get_deleted_theses(db)

# 3. Create a new thesis
@router.post("/theses/add", response_model=schemas.ThesisOut)
def create_thesis(thesis: schemas.ThesisCreate, db: Session = Depends(get_db)):
    return crud.create_thesis(db, thesis)

# 4. Get thesis by ID
@router.get("/theses/{thesis_id}", response_model=schemas.ThesisOut)
def read_thesis(thesis_id: int, db: Session = Depends(get_db)):
    db_thesis = crud.get_thesis(db, thesis_id)
    if db_thesis is None:
        raise HTTPException(status_code=404, detail="Thesis not found")
    return db_thesis

# 5. Update thesis by ID
@router.put("/theses/{thesis_id}", response_model=schemas.ThesisOut)
def update_thesis(thesis_id: int, thesis: schemas.ThesisCreate, db: Session = Depends(get_db)):
    db_thesis = crud.get_thesis(db, thesis_id)
    if db_thesis is None:
        raise HTTPException(status_code=404, detail="Thesis not found")
    
    update_data = thesis.dict(exclude_unset=True)
    # Prevent updating date_uploaded
    update_data.pop('date_uploaded', None)
    
    for key, value in update_data.items():
        setattr(db_thesis, key, value)
    
    db.commit()
    db.refresh(db_thesis)
    return db_thesis

# 6. Soft-delete thesis
@router.delete("/theses/{thesis_id}")
def delete_thesis(thesis_id: int, db: Session = Depends(get_db)):
    if crud.delete_thesis(db, thesis_id):
        return {"message": "Thesis deleted successfully"}
    raise HTTPException(status_code=404, detail="Thesis not found")

# 7. Restore deleted thesis
@router.put("/theses/{thesis_id}/restore", response_model=schemas.ThesisOut)
def restore_thesis_endpoint(thesis_id: int, db: Session = Depends(get_db)):
    restored = crud.restore_thesis(db, thesis_id)
    if not restored:
        raise HTTPException(status_code=404, detail="Thesis not found or not deleted")
    return restored
