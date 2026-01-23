from datetime import datetime, timedelta
from os import getenv

import sqlalchemy
import uvicorn

from fastapi import FastAPI, HTTPException

from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from dotenv import load_dotenv
from jose import jwt

load_dotenv()

# Db config
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
    refresh_token = Column(String)
Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI()

# CRUD
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
private_key=getenv("SECRET_KEY")

def create_access_token(data: dict):
    to_encode=data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, private_key, algorithm=ALGORITHM),expire
def create_refresh_token(data: dict):
    db = SessionLocal()
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    refresh = jwt.encode(to_encode, private_key, algorithm=ALGORITHM)
    db.execute(
        text("UPDATE users SET refresh_token= :refresh WHERE email = :email "),
        {"refresh": refresh, "email": data["email"]}
    )
    db.commit()
    return refresh,expire

@app.post("/AUTH/LOGIN")
async def login(email,password):
    db=SessionLocal()
    ph = PasswordHasher()
    result = db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    ).mappings().fetchone()
    if result is None :
        raise HTTPException(status_code=404, detail="User not found")
    #return ph.verify(heldPassword,password)
    heldPassword = result["password_hash"]
    try:
        ph.verify(heldPassword,password)
        refresh,refresh_expire=create_refresh_token({"email":email , "password": password})
        access,access_expire=create_access_token({"id":result["id"],"email":email , "password": password})
        #acces printed for test purposes on auth/me
        print(access)
        return refresh, access, refresh_expire
    except VerifyMismatchError:
        raise HTTPException(status_code=404, detail="Email password combination invalid")
    finally:
        db.close()

@app.post("/AUTH/REFRESH")
async def refresh(refresh_token):
    new_access=create_access_token({"refresh":refresh_token})
    return  new_access

@app.post("/AUTH/LOGOUT")
async def logout(email):
    try:
        db=SessionLocal()
        db.execute(text("UPDATE users SET refresh_token = :refresh WHERE email = :email"),{"refresh":None,"email":email})
        db.commit()
        return {"status": "success"}
    except sqlalchemy.exc.SQLAlchemyError:
        raise HTTPException(status_code=404, detail="SQL ERROR!")

if __name__ == "__main__":
    uvicorn.run(app)

@app.get("/AUTH/ME")
async def me(access_token):
    try:
        db=SessionLocal()
        derived_id= jwt.decode(access_token, private_key, algorithms=[ALGORITHM])["id"]
        result = db.execute(text("SELECT * FROM users WHERE id = :id "),{"id":derived_id}).mappings().fetchone()
        print(result["id"], result["email"], result["role"])
        return result["id"], result["email"], result["role"]
    except sqlalchemy.exc.SQLAlchemyError:
        raise HTTPException(status_code=404, detail="SQL ERROR!")


