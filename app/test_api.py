import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.constants import DATABASE_URL

@pytest.fixture
def db():
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

