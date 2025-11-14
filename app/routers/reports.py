from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, database
from datetime import datetime, timedelta

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/reports/stats/")
def get_statistics(db: Session = Depends(get_db)):
    # Get total number of theses
    total_theses = db.query(func.count(models.Thesis.id)).scalar()
    
    # Get total number of users
    total_users = db.query(func.count(models.User.id)).scalar()
    
    # Get thesis counts by program
    theses_by_program = (
        db.query(
            models.Thesis.program_course,
            func.count(models.Thesis.id).label('count')
        )
        .group_by(models.Thesis.program_course)
        .all()
    )
    
    # Get new users created this month
    first_day_of_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    new_users_this_month = (
        db.query(func.count(models.User.id))
        .filter(models.User.date_registered >= first_day_of_month)
        .scalar() or 0
    )
    
    # Get unique active users in the last 7 days
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    active_users_this_week = (
        db.query(func.count(func.distinct(models.SearchHistory.student_id)))
        .filter(models.SearchHistory.date_accessed >= seven_days_ago)
        .scalar() or 0
    )

    # Get most accessed theses
    most_accessed = (
        db.query(
            models.SearchHistory.thesis_id,
            models.SearchHistory.book_title,
            func.count(models.SearchHistory.id).label('access_count')
        )
        .group_by(models.SearchHistory.thesis_id, models.SearchHistory.book_title)
        .order_by(func.count(models.SearchHistory.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_theses": total_theses,
        "total_users": total_users,
        "new_users_this_month": new_users_this_month,
        "active_users_this_week": active_users_this_week,
        "theses_by_program": [
            {"program": program, "count": count}
            for program, count in theses_by_program
        ],
        "most_accessed": [
            {
                "thesis_id": thesis_id,
                "title": title,
                "access_count": count
            }
            for thesis_id, title, count in most_accessed
        ]
    }
