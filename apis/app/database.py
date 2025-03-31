from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from .config import DATABASE_URL

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# OYRDB password - Postgres@1

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)
