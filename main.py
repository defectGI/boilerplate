from datetime import datetime
import uvicorn
from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher


# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./datalocal/database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email= Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role= Column(String)
    is_active=Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI()

# CRUD operations
@app.post("/AUTH/LOGIN")
async def login(email, password):
    db=SessionLocal()
    ph = PasswordHasher()
    heldPassword = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    #return ph.verify(heldPassword,password)
    if ph.verify(heldPassword,password):
        print("aaaa")
    else:
        print("bbb")
if __name__ == "__main__":
    uvicorn.run(app)