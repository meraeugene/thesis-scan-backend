# app/migrate_data.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Thesis, User, Bookmark, SearchHistory, Librarian
from app.database import Base

# ----- Local database -----
LOCAL_DB_URL = "postgresql://thesiscan_admin:password@localhost:5432/thesiscan_db"
local_engine = create_engine(LOCAL_DB_URL)
LocalSession = sessionmaker(bind=local_engine)
local_session = LocalSession()

# ----- Railway database -----
RAILWAY_DB_URL = "postgresql://postgres:qWxdxHPwqEEIBZckfQsWIdUaQKDseiaD@gondola.proxy.rlwy.net:13656/railway"
railway_engine = create_engine(RAILWAY_DB_URL)
RailwaySession = sessionmaker(bind=railway_engine)
railway_session = RailwaySession()

# Make sure tables exist in Railway
Base.metadata.create_all(bind=railway_engine)

# Helper function to copy rows safely
def migrate_table(local_session, railway_session, model):
    all_rows = local_session.query(model).all()
    for row in all_rows:
        # Remove SQLAlchemy internal attributes
        data = {k: v for k, v in row.__dict__.items() if not k.startswith('_')}
        railway_session.add(model(**data))
    railway_session.commit()
    print(f"✅ Migrated {len(all_rows)} rows from {model.__tablename__}")

# ----- Migrate all models -----
migrate_table(local_session, railway_session, Thesis)
migrate_table(local_session, railway_session, User)
migrate_table(local_session, railway_session, Bookmark)
migrate_table(local_session, railway_session, SearchHistory)
migrate_table(local_session, railway_session, Librarian)

print("🎉 All data migrated successfully!")
