import pytest

pytestmark = pytest.mark.django_db


def test_hotel_list_returns_all_hotels(api_client, hotel_factory):
    """Список должен возвращать все созданные отели"""
    hotel_factory()
    hotel_factory()
    hotel_factory()

    resp = api_client.get("/api/hotels/list/")
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == 3


def test_hotel_list_sorted_by_name_asc(api_client, hotel_factory):
    """Проверка сортировки по имени (A → Z)"""
    hotel_factory(name="Bravo")
    hotel_factory(name="Alpha")
    hotel_factory(name="Charlie")

    resp = api_client.get("/api/hotels/list/?ordering=name")

    names = [h["name"] for h in resp.json()]
    assert names == ["Alpha", "Bravo", "Charlie"]


def test_hotel_list_sorted_by_name_desc(api_client, hotel_factory):
    """Проверка сортировки по имени (Z → A)"""
    hotel_factory(name="Bravo")
    hotel_factory(name="Alpha")
    hotel_factory(name="Charlie")

    resp = api_client.get("/api/hotels/list/?ordering=-name")

    names = [h["name"] for h in resp.json()]
    assert names == ["Charlie", "Bravo", "Alpha"]


def test_hotel_list_sorted_by_created_at_desc_default(api_client, hotel_factory):
    """По умолчанию сортировка: created_at DESC"""
    hotel_factory(created_at="2020-01-01")
    hotel_factory(created_at="2030-01-01")

    resp = api_client.get("/api/hotels/list/")

    dates = [h["created_at"] for h in resp.json()]
    assert dates[0].startswith("2030")
    assert dates[1].startswith("2020")


def test_hotel_list_sorted_by_created_at_asc(api_client, hotel_factory):
    """Проверка сортировки created_at ASC"""
    hotel_factory(created_at="2020-01-01")
    hotel_factory(created_at="2030-01-01")

    resp = api_client.get("/api/hotels/list/?ordering=created_at")

    dates = [h["created_at"] for h in resp.json()]
    assert dates[0].startswith("2020")
    assert dates[1].startswith("2030")


def test_hotel_create_valid(api_client):
    """Создание отеля"""
    payload = {
        "name": "New Hotel",
        "address": "Some street 1",
        "description": "Nice place",
    }

    resp = api_client.post("/api/hotels/create/", payload, format="json")
    assert resp.status_code == 201

    data = resp.json()
    assert data["name"] == "New Hotel"
    assert data["address"] == "Some street 1"
    assert data["description"] == "Nice place"
    assert "created_at" in data


def test_hotel_create_missing_name(api_client):
    """name — обязательное поле"""
    payload = {"address": "Some street 1", "description": "Nice"}

    resp = api_client.post("/api/hotels/create/", payload, format="json")
    assert resp.status_code == 400
    assert "name" in resp.json()


def test_hotel_create_missing_address(api_client):
    """address — обязательное поле"""
    payload = {"name": "Test Hotel", "description": "Nice"}

    resp = api_client.post("/api/hotels/create/", payload, format="json")
    assert resp.status_code == 400
    assert "address" in resp.json()


def test_hotel_delete(api_client, hotel_factory):
    """Удаление отеля"""
    hotel = hotel_factory()

    resp = api_client.delete(f"/api/hotels/{hotel.id}/delete/")
    assert resp.status_code == 200

    # Проверяем что отеля нет в списке
    resp2 = api_client.get("/api/hotels/list/")
    ids = [h["id"] for h in resp2.json()]
    assert hotel.id not in ids
