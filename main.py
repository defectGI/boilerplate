from datetime import datetime
import uvicorn
from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


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
    result = db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    ).fetchone()
    if(result is None):
        print("Kullanıcı yok")
    #return ph.verify(heldPassword,password)
    heldPassword = result[2]
    try:
        ph.verify(heldPassword,password)
        print("aaaa")
    except VerifyMismatchError:
        print("bbb")
if __name__ == "__main__":
    uvicorn.run(app)