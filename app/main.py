import ipaddress
from datetime import datetime, timedelta
from os import getenv

import sqlalchemy
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import Request
from sqlalchemy import Column, Integer, String, DateTime, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from dotenv import load_dotenv
from jose import jwt


import constants

load_dotenv()

#Config
DATABASE_URL = constants.DATABASE_URL
ALGORITHM = constants.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = constants.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = constants.REFRESH_TOKEN_EXPIRE_DAYS
SECRET_KEY = getenv(constants.ENV_SECRET_KEY)


# SQL strings (readable)
SQL_SELECT_USER_BY_EMAIL = constants.SQL_SELECT_USER_BY_EMAIL
SQL_SELECT_USER_BY_ID = constants.SQL_SELECT_USER_BY_ID
SQL_UPDATE_REFRESH_BY_EMAIL = constants.SQL_UPDATE_REFRESH_BY_EMAIL
SQL_UPDATE_REFRESH_NULL_BY_EMAIL = constants.SQL_UPDATE_REFRESH_NULL_BY_EMAIL

# DB setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String)
    is_active = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    refresh_token = Column(String)
    last_login_at = Column(DateTime)


Base.metadata.create_all(bind=engine)

# App
app = FastAPI()

@app.middleware("http")
async def secure_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"

    return response


# Token helpers
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM), expire


def create_refresh_token(data: dict):
    db = SessionLocal()
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})

    refresh = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # store refresh in DB (same behavior)
    db.execute(text(constants.refresh_token_creation_query), {"refresh": refresh, "email": data["email"]})
    db.commit()
    db.close()

    return refresh, expire

def failed_login(db, email, request: Request):
    ip = request.client.host
    db.execute(text(constants.SQL_UPDATE_LOGIN_ATTEMPT),
               {"email": email, "ip_address": ip})
    db.commit()
    return 0
# Routes
@app.post(constants.PATH_AUTH_LOGIN)
async def login(email, password, request: Request):
    db = SessionLocal()

    ip=request.client.host
    number_of_attempts = db.execute(text(constants.SQL_COUNT_LOGINS_LAST_FIVE_MINUTES),{"ip_address": ip}).fetchone()
    attempts = number_of_attempts[0] if number_of_attempts else 0
    if attempts > 5:
        exit()
    ph = PasswordHasher()

    try:
        # fetch user by email
        result = (
            db.execute(text(constants.SQL_SELECT_USER_BY_EMAIL), {"email": email})
            .mappings()
            .fetchone()
        )

        if result is None:
            raise HTTPException(status_code=404, detail="User not found")

        held_password_hash = result["password_hash"]

        # verify password
        ph.verify(held_password_hash, password)

        refresh, refresh_expire = create_refresh_token({"email": email, "password": password})
        access, access_expire = create_access_token({"id": result["id"], "email": email, "password": password})

        # printed for test purposes on auth/me
        print(access)
        db.execute(text(constants.SQL_UPDATE_SET_USER_ACTIVE), {"email": email})

        db.execute(text(constants.SQL_UPDATE_LAST_LOGIN), {"date":datetime.now(), "email": email})

        db.commit()
        db.close()
        print("aaa")
        return refresh, access, refresh_expire
    except VerifyMismatchError:
        failed_login(db, email,request)
        db.close()
        raise HTTPException(status_code=404, detail="Email password combination invalid")

@app.post(constants.PATH_AUTH_REFRESH)
async def refresh(refresh_token):
    new_access = create_access_token({"refresh": refresh_token})
    return new_access


@app.post(constants.PATH_AUTH_LOGOUT)
async def logout(email):
    db = SessionLocal()
    try:
        db.execute(text(SQL_UPDATE_REFRESH_NULL_BY_EMAIL), {"refresh": None, "email": email})
        db.execute(text(constants.SQL_UPDATE_SET_USER_INACTIVE), {"email": email})
        db.commit()
        return {"status": "success"}
    except sqlalchemy.exc.SQLAlchemyError:
        raise HTTPException(status_code=404, detail="SQL ERROR!")
    finally:
        db.close()

@app.get(constants.PATH_AUTH_ME)
async def me(access_token):
    db = SessionLocal()
    try:
        derived_id = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])["id"]

        result = (
            db.execute(text(SQL_SELECT_USER_BY_ID), {"id": derived_id})
            .mappings()
            .fetchone()
        )

        print(result["id"], result["email"], result["role"])
        return result["id"], result["email"], result["role"]

    except sqlalchemy.exc.SQLAlchemyError:
        raise HTTPException(status_code=404, detail="SQL ERROR!")
    finally:
        db.close()
@app.get(constants.PATH_HEALTH)
async def health():
    try:
        db = SessionLocal()
        db.execute(text(constants.SQL_SELECT_HEALTH))
        db_status="healthy"
    except:
        db_status="unhealthy"

    if(db_status == "healthy"):
        return {"status": "success, database is healthy"}
    else:
        return {"status": "unhealthy database is unhealthy"}

if __name__ == "__main__":
    uvicorn.run(app)
