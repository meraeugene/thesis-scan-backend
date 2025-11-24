from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app import models, crud
from app.database import get_db

router = APIRouter()

@router.get("/reports/stats/")
def get_statistics(db: Session = Depends(get_db)):
    # Get all theses with their view counts
    theses_with_views = crud.get_theses_with_views(db)  # returns list of ThesisWithViews
    
    # Total theses and total views
    total_theses = len(theses_with_views)
    total_views = sum(t.views for t in theses_with_views)
    
    # Most accessed theses (top 5 by views)
    most_accessed_sorted = sorted(theses_with_views, key=lambda t: t.views, reverse=True)[:5]
    most_accessed_data = [
        {
            "thesis_id": t.id,
            "title": t.title,
            "views": t.views
        }
        for t in most_accessed_sorted
    ]
    
    # Total users
    total_users = db.query(func.count(models.User.id)).scalar() or 0
    
    # Theses count by program
    theses_by_program = (
        db.query(
            models.Thesis.program_course,
            func.count(models.Thesis.id).label("count")
        )
        .group_by(models.Thesis.program_course)
        .all()
    )
    
    # New users this month
    first_day_of_month = datetime.now().replace(day=1)
    new_users_this_month = (
        db.query(func.count(models.User.id))
        .filter(models.User.date_registered >= first_day_of_month)
        .scalar() or 0
    )
    
    # Active users in the last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    active_users_this_week = (
        db.query(func.count(func.distinct(models.SearchHistory.student_id)))
        .filter(models.SearchHistory.date_accessed >= seven_days_ago)
        .scalar() or 0
    )

    return {
        "total_theses": total_theses,
        "total_views": total_views,
        "total_users": total_users,
        "new_users_this_month": new_users_this_month,
        "active_users_this_week": active_users_this_week,
        "theses_by_program": [
            {"program": program, "count": count} for program, count in theses_by_program
        ],
        "most_accessed": most_accessed_data
    }
