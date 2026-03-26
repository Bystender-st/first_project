import pytest

pytestmark = pytest.mark.django_db


def test_room_list_returns_all_rooms(api_client, room_factory):
    """Список должен возвращать все созданные комнаты"""
    room_factory()
    room_factory()
    room_factory()

    resp = api_client.get("/api/rooms/list/")
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == 3


def test_room_list_sorted_by_price_asc(api_client, room_factory):
    """Сортировка цены от меньшего к большему"""
    room_factory(price_per_night=100)
    room_factory(price_per_night=300)
    room_factory(price_per_night=200)

    resp = api_client.get("/api/rooms/list/?ordering=price_per_night")

    prices = [float(r["price_per_night"]) for r in resp.json()]
    assert prices == [100, 200, 300]


def test_room_list_sorted_by_price_desc(api_client, room_factory):
    """Сортировка цены от большего к меньшему"""
    room_factory(price_per_night=100)
    room_factory(price_per_night=300)
    room_factory(price_per_night=200)

    resp = api_client.get("/api/rooms/list/?ordering=-price_per_night")

    prices = [float(r["price_per_night"]) for r in resp.json()]
    assert prices == [300, 200, 100]


def test_room_list_sorted_by_created_at_desc_default(api_client, room_factory):
    """По умолчанию сортировка: created_at DESC"""
    room_factory(created_at="2020-01-01")
    room_factory(created_at="2030-01-01")

    resp = api_client.get("/api/rooms/list/")
    dates = [r["created_at"] for r in resp.json()]

    assert dates[0].startswith("2030")
    assert dates[1].startswith("2020")


def test_room_list_sorted_by_created_at_asc(api_client, room_factory):
    """Сортировка created_at ASC"""
    room_factory(created_at="2020-01-01")
    room_factory(created_at="2030-01-01")

    resp = api_client.get("/api/rooms/list/?ordering=created_at")
    dates = [r["created_at"] for r in resp.json()]

    assert dates[0].startswith("2020")
    assert dates[1].startswith("2030")


def test_room_create_valid(api_client, hotel_factory):
    """Создание комнаты"""
    hotel = hotel_factory()

    payload = {
        "hotel": hotel.id,
        "number": "101",
        "capacity": 2,
        "price_per_night": "150.00",
        "is_available": True,
    }

    resp = api_client.post("/api/rooms/create/", payload, format="json")
    assert resp.status_code == 201

    data = resp.json()
    assert data["number"] == "101"
    assert data["capacity"] == 2
    assert float(data["price_per_night"]) == 150.00
    assert data["hotel"] == hotel.id


def test_room_create_missing_required_fields(api_client):
    """Проверка обязательных полей (capacity НЕ обязательно, default=1)"""
    resp = api_client.post("/api/rooms/create/", {}, format="json")

    assert resp.status_code == 400
    data = resp.json()

    assert "hotel" in data
    assert "number" in data
    assert "price_per_night" in data

    assert "capacity" not in data
    assert "is_available" not in data


def test_room_delete(api_client, room_factory):
    """Удаление комнаты"""
    room = room_factory()

    resp = api_client.delete(f"/api/rooms/delete/{room.id}/")
    assert resp.status_code == 200

    resp2 = api_client.get("/api/rooms/list/")
    ids = [r["id"] for r in resp2.json()]
    assert room.id not in ids
