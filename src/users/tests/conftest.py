import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """DRF APIClient, общий для всех tests."""
    return APIClient()


@pytest.fixture
def create_user():
    """
    Фабрика для создания пользователей корректным способом:
    User.objects.create_user() автоматически хеширует пароль.
    """

    def _create_user(**kwargs):
        password = kwargs.pop("password", "strongpass123")
        return User.objects.create_user(password=password, **kwargs)

    return _create_user


@pytest.fixture
def user(create_user):
    """Создаёт обычного пользователя"""
    return create_user(email="test@example.com", username="testuser")


@pytest.fixture
def auth_client(api_client, create_user):
    """
    Возвращает client, авторизованный через force_authenticate (для тестов /me).
    """
    user = create_user(
        email="john@example.com", username="john", password="strongpass123"
    )
    api_client.force_authenticate(user)
    return api_client
