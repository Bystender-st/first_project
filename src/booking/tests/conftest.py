import pytest
from rest_framework.test import APIClient

from .factories import BookingFactory, HotelFactory, RoomFactory


@pytest.fixture
def api_client(django_user_model):
    user = django_user_model.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def hotel_factory():
    def _create(**kwargs):
        return HotelFactory.create(**kwargs)

    return _create


@pytest.fixture
def room_factory():
    def _create(**kwargs):
        return RoomFactory.create(**kwargs)

    return _create


@pytest.fixture
def booking_factory():
    def _create(**kwargs):
        return BookingFactory.create(**kwargs)

    return _create
