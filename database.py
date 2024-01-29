from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import load_config

config_url = load_config('.env')
SQLALCHEMY_DATABASE_URL = config_url.db.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
