from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/theses/", response_model=schemas.ThesisOut)
def create_thesis(thesis: schemas.ThesisCreate, db: Session = Depends(get_db)):
    return crud.create_thesis(db, thesis)

@router.get("/theses/{thesis_id}", response_model=schemas.ThesisOut)
def read_thesis(thesis_id: int, db: Session = Depends(get_db)):
    db_thesis = crud.get_thesis(db, thesis_id)
    if db_thesis is None:
        raise HTTPException(status_code=404, detail="Thesis not found")
    return db_thesis

# Add GET /theses endpoint for listing all theses
@router.get("/theses", response_model=list[schemas.ThesisOut])
def list_theses(db: Session = Depends(get_db)):
    return crud.get_theses(db)

@router.put("/theses/{thesis_id}", response_model=schemas.ThesisOut)
def update_thesis(thesis_id: int, thesis: schemas.ThesisCreate, db: Session = Depends(get_db)):
    db_thesis = crud.get_thesis(db, thesis_id)
    if db_thesis is None:
        raise HTTPException(status_code=404, detail="Thesis not found")
    
    update_data = thesis.dict(exclude_unset=True)
    # Don't update date_uploaded field
    update_data.pop('date_uploaded', None)
    
    for key, value in update_data.items():
        setattr(db_thesis, key, value)
    
    db.commit()
    db.refresh(db_thesis)
    return db_thesis

@router.delete("/theses/{thesis_id}")
def delete_thesis(thesis_id: int, db: Session = Depends(get_db)):
    if crud.delete_thesis(db, thesis_id):
        return {"message": "Thesis deleted successfully"}
    raise HTTPException(status_code=404, detail="Thesis not found")