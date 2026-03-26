import pytest
from model_bakery import baker
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


# REGISTRATION TESTS
def test_register_user_success():
    client = APIClient()

    payload = {
        "username": "testuser",
        "email": "test@mail.com",
        "password": "strongpass123",
    }

    resp = client.post("/api/users/register/", payload)

    assert resp.status_code == 201
    data = resp.json()

    assert data["email"] == "test@mail.com"
    assert data["username"] == "testuser"


def test_register_duplicate_email_fails():
    baker.make("users.User", email="test@mail.com")

    client = APIClient()
    payload = {
        "username": "user2",
        "email": "test@mail.com",
        "password": "123456",
    }

    resp = client.post("/api/users/register/", payload)

    assert resp.status_code == 400
    assert "email" in resp.json()


def test_register_missing_fields():
    client = APIClient()

    resp = client.post("/api/users/register/", {"email": "a@mail.com"})

    assert resp.status_code == 400
    assert "password" in resp.json()
    assert "username" in resp.json()


# login
def test_login_success():
    user = baker.make("users.User", email="login@test.com")
    user.set_password("pass12345")
    user.save()

    client = APIClient()
    resp = client.post(
        "/api/users/login/", {"email": "login@test.com", "password": "pass12345"}
    )

    assert resp.status_code == 200
    data = resp.json()

    assert "access" in data
    assert "refresh" in data


def test_login_wrong_password():
    user = baker.make("users.User", email="wrong@test.com")
    user.set_password("rightpass")
    user.save()

    client = APIClient()

    resp = client.post(
        "/api/users/login/", {"email": "wrong@test.com", "password": "wrongpass"}
    )

    assert resp.status_code == 401


def test_login_nonexistent_email():
    client = APIClient()

    resp = client.post("/api/users/login/", {"email": "no@user.com", "password": "any"})

    assert resp.status_code == 401


# refresh
def test_refresh_token_success():
    user = baker.make("users.User", email="refresh@test.com")
    user.set_password("pass123")
    user.save()

    client = APIClient()

    # получить refresh token
    login = client.post(
        "/api/users/login/", {"email": "refresh@test.com", "password": "pass123"}
    )

    refresh_token = login.json()["refresh"]

    # обновление
    resp = client.post("/api/users/refresh/", {"refresh": refresh_token})

    assert resp.status_code == 200
    assert "access" in resp.json()


def test_refresh_token_invalid():
    client = APIClient()

    resp = client.post("/api/users/refresh/", {"refresh": "not-a-real-token"})

    assert resp.status_code == 401


# user me
def test_user_me_success():
    user = baker.make("users.User", email="me@test.com")
    user.set_password("pass123")
    user.save()

    client = APIClient()

    login = client.post(
        "/api/users/login/", {"email": "me@test.com", "password": "pass123"}
    )

    access = login.json()["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    resp = client.get("/api/users/me/")

    assert resp.status_code == 200
    data = resp.json()

    assert data["email"] == "me@test.com"


def test_user_me_unauthorized_no_token():
    client = APIClient()

    resp = client.get("/api/users/me/")

    assert resp.status_code == 401


def test_user_me_invalid_token():
    client = APIClient()

    client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.123")

    resp = client.get("/api/users/me/")

    assert resp.status_code == 401
