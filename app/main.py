from datetime import datetime, timedelta, timezone
from os import getenv

import sqlalchemy
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.params import Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from dotenv import load_dotenv
import constants
from tables import SessionLocal, LoginRequest, get_db
from jose import jwt, JWTError

load_dotenv()

DATABASE_URL = constants.DATABASE_URL
ALGORITHM = constants.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = constants.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = constants.REFRESH_TOKEN_EXPIRE_DAYS
SECRET_KEY = constants.ENV_SECRET_KEY

app = FastAPI()

@app.middleware("http")
async def secure_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


def create_access_token(id: int, db):
    user = db.execute(text(constants.SQL_SELECT_USER_BY_ID), {"id": id}).mappings().fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı acces_token üretimi için bulunamadı")
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "exp": expire
    }
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return access_token, expire


def create_refresh_token(email, db):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh = jwt.encode({"email":email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    db.execute(text(constants.REFRESH_TOKEN_CREATION_QUERY), {"refresh": refresh, "expire": expire, "email": email})
    return refresh, expire

def failed_login(db, email, request: Request):
    ip = request.client.host
    db.execute(text(constants.SQL_UPDATE_LOGIN_ATTEMPT),
               {"email": email, "ip_address": ip})
    return 0
# Routes
@app.post(constants.PATH_AUTH_LOGIN)
async def login(body:LoginRequest, request: Request,db = Depends(get_db)):
    email = body.email
    password = body.password
    ph = PasswordHasher()
    ip=request.client.host
    number_of_attempts = db.execute(text(constants.SQL_COUNT_LOGINS_LAST_FIVE_MINUTES),{"ip_address": ip}).fetchone()
    attempts = number_of_attempts[0] if number_of_attempts else 0
    if attempts > 5:
        raise HTTPException(status_code=403, detail="This ip is locked")
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

        refresh_token, refresh_expire = create_refresh_token(result["email"], db)
        access, access_expire = create_access_token(result["id"], db)

        db.execute(text(constants.SQL_UPDATE_SET_USER_ACTIVE), {"email": email})

        db.execute(text(constants.SQL_UPDATE_LAST_LOGIN), {"date":datetime.now(timezone.utc), "email": email})

        print("aaa")
        return {"refresh_token":refresh_token, "access_token":access, "refresh_expire_at":refresh_expire}
    except VerifyMismatchError:
        failed_login(db, email,request)
        raise HTTPException(status_code=401, detail="Email password combination invalid")

@app.post(constants.PATH_AUTH_REFRESH)
async def refresh(refresh_token, db = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["email"]
        user = db.execute(text(constants.SQL_SELECT_USER_BY_EMAIL), {"email": email}).mappings().fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        validate = db.execute(text(constants.SQL_VALIDATE_REFRESH), {"id": user["id"], "token": refresh_token}).fetchone()
    except JWTError:
        raise HTTPException(status_code=404, detail="Refresh token error")
    if not validate:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    access, access_expire = create_access_token(user["id"],db)
    return {"access_token" : access, "access_expire" : access_expire}


@app.post(constants.PATH_AUTH_LOGOUT)
async def logout(email,db = Depends(get_db)):
    try:
        db.execute(text(constants.SQL_UPDATE_REFRESH_NULL_BY_EMAIL), {"refresh": None, "email": email})
        db.execute(text(constants.SQL_UPDATE_SET_USER_INACTIVE), {"email": email})

        return {"status": "success"}
    except sqlalchemy.exc.SQLAlchemyError:
        raise HTTPException(status_code=404, detail="SQL ERROR!")



@app.get(constants.PATH_AUTH_ME)
async def me(access_token,db = Depends(get_db)):
    try:
        derived_email = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])["email"]
        result = (
            db.execute(text(constants.SQL_SELECT_USER_BY_EMAIL), {"email": derived_email}).mappings().fetchone()
        )
        return result["id"], result["email"], result["role"]
    except JWTError:
        raise HTTPException(status_code=403, detail="Refresh token error")




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
