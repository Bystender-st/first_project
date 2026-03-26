import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_register_user_success(api_client):
    payload = {
        "username": "john",
        "email": "john@example.com",
        "password": "verystrongpass123",
    }

    response = api_client.post("/api/users/register/", payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["username"] == "john"
    assert data["email"] == "john@example.com"
    assert "password" not in data

    assert User.objects.filter(email="john@example.com").exists()


@pytest.mark.django_db
def test_register_user_duplicate_email(api_client):
    User.objects.create_user(
        username="existing", email="john@example.com", password="123456"
    )

    payload = {
        "username": "newuser",
        "email": "john@example.com",
        "password": "newpass123",
    }

    response = api_client.post("/api/users/register/", payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.json()


@pytest.mark.django_db
def test_register_user_missing_fields(api_client):
    payload = {"email": "no_username@example.com", "password": "password123"}

    response = api_client.post("/api/users/register/", payload)

    assert response.status_code == 400
    assert "username" in response.json()
