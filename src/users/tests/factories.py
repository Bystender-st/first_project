import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker

User = get_user_model()


@pytest.fixture
def user():
    """
    Базовый пользователь без гарантированного пароля.
    Подходит для тестов, где НЕ нужно логиниться.
    """
    return baker.make(User)


@pytest.fixture
def user_with_password():
    """
    Пользователь для тестов логина.
    Устанавливаем пароль вручную → baker.make не делает этого.
    """
    user = baker.make(User, email="user@test.com")
    user.set_password("strongpass123")
    user.save()
    return user
