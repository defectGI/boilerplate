
import pytest
from argon2 import PasswordHasher
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from main import app
from tables import get_db


import constants
from constants import TEST_DATABASE_URL


@pytest.fixture
def db():
    engine = create_engine(TEST_DATABASE_URL)
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

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    ph = PasswordHasher()
    password_hash = ph.hash("dogru_sifre")
    db.execute(text(constants.INSERT_TEST_USER),{"email": "test@user.com","password_hash": password_hash,"role":"user","is_active":0})
    db.commit()
    return ({"email": "test@user.com", "password" : password_hash})

def test_login_success(test_user, client):
    response = client.post("/auth/login", json={"email": test_user["email"], "password": "dogru_sifre"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "refresh_expire_at" in data

def test_login_failure(test_user, client):
    response = client.post(constants.PATH_AUTH_LOGIN,json={"email": test_user["email"], "password": "yanlis_password123"})
    assert response.status_code == 401

def test_input_validation_failure(test_user, client):
    response = client.post(constants.PATH_AUTH_LOGIN,json={"password": test_user["password"]})
    assert response.status_code == 422

def test_refresh_success(test_user, client):
    login_response = client.post(constants.PATH_AUTH_LOGIN, json={"email": test_user["email"], "password": "dogru_sifre"})
    assert login_response.status_code == 200
    refresh_token= login_response.json()["refresh_token"]
    response = client.post(constants.PATH_AUTH_REFRESH, json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "access_expire" in response.json()
    does_work = client.get(constants.PATH_AUTH_ME,params={"access_token": response.json()["access_token"]})
    assert does_work.status_code == 200

def test_refresh_failure(test_user, client):
    response = client.post(constants.PATH_AUTH_REFRESH, json={"refresh_token": "sallamasyon"})
    assert response.status_code == 422

def test_unauthorized_access(test_user, client):
    response = client.get(constants.PATH_AUTH_ME,params={"access_token": "cokyanlisaccess"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Refresh token error"
