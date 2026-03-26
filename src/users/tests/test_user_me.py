import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_user_me_authenticated(api_client):
    user = User.objects.create_user(
        username="john", email="john@example.com", password="strongpass123"
    )

    api_client.force_authenticate(user=user)

    response = api_client.get("/api/users/me/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["username"] == user.username


@pytest.mark.django_db
def test_user_me_unauthenticated(api_client):
    response = api_client.get("/api/users/me/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
