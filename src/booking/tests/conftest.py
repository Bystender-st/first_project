import pytest
from rest_framework.test import APIClient

from .factories import BookingFactory, HotelFactory, RoomFactory


@pytest.fixture
def api_client():
    return APIClient()


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
