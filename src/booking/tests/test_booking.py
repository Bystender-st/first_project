from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def _future_date(days: int) -> str:
    """Возвращает ISO-строку для даты в будущем на days дней."""
    return (date.today() + timedelta(days=days)).isoformat()


def extract_page(resp):
    """
    Нормализует ответ: если API вернул пагинацию -> возвращаем dict,
    если вернул список (на всякий случай) -> возвращаем {'count': len, 'results': list}
    """
    data = resp.json()
    if isinstance(data, dict) and "results" in data:
        return data
    # старый стиль (список) — привести к paginated shape
    return {"count": len(data), "results": data}


def test_booking_list_empty(api_client):
    """Если бронирований нет — возвращается пустая страница (count=0, results=[])"""
    resp = api_client.get("/api/bookings/list/")
    assert resp.status_code == 200

    page = extract_page(resp)
    assert page["count"] == 0
    assert page["results"] == []


def test_booking_list_multiple(api_client, booking_factory):
    """Создаём несколько броней (принадлежат авторизованному пользователю) и проверяем, что они возвращаются"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    bookings = booking_factory(_quantity=5, user=owner)

    resp = api_client.get("/api/bookings/list/")
    assert resp.status_code == 200

    page = extract_page(resp)
    assert page["count"] == 5
    results = page["results"]
    assert len(results) == 5

    returned_ids = {b["booking_id"] for b in results}
    expected_ids = {b.id for b in bookings}
    assert returned_ids == expected_ids


def test_booking_filter_by_hotel(
    api_client, hotel_factory, room_factory, booking_factory
):
    """Фильтр: возвращаются только брони указанного отеля (и только своего пользователя)"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    hotel1 = hotel_factory()
    hotel2 = hotel_factory()

    room1 = room_factory(hotel=hotel1)
    room2 = room_factory(hotel=hotel2)

    b1 = booking_factory(room=room1, user=owner)
    booking_factory(room=room2, user=owner)

    resp = api_client.get(f"/api/bookings/list/?hotel_id={hotel1.id}")
    assert resp.status_code == 200

    page = extract_page(resp)
    results = page["results"]
    assert len(results) == 1
    assert results[0]["booking_id"] == b1.id


def test_booking_sort_by_room_asc(api_client, room_factory, booking_factory):
    """Сортировка по room.id (возрастание)"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    rooms = room_factory(_quantity=3)
    rooms_sorted = sorted(rooms, key=lambda r: r.id)

    for r in rooms_sorted:
        booking_factory(
            room=r, user=owner, start_date=_future_date(10), end_date=_future_date(11)
        )

    resp = api_client.get("/api/bookings/list/?order=room")
    assert resp.status_code == 200

    page = extract_page(resp)
    results = page["results"]

    extracted = [b["room"] for b in results]
    expected = [r.id for r in rooms_sorted]
    assert extracted == expected


def test_booking_sort_by_room_desc(api_client, room_factory, booking_factory):
    """Сортировка по room.id (убывание)"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    rooms = room_factory(_quantity=3)
    rooms_sorted_desc = sorted(rooms, key=lambda r: r.id, reverse=True)

    for r in rooms_sorted_desc:
        booking_factory(
            room=r, user=owner, start_date=_future_date(20), end_date=_future_date(21)
        )

    resp = api_client.get("/api/bookings/list/?order=-room")
    assert resp.status_code == 200

    page = extract_page(resp)
    results = page["results"]

    extracted = [b["room"] for b in results]
    expected = [r.id for r in rooms_sorted_desc]
    assert extracted == expected


def test_booking_sort_by_hotel_asc(
    api_client, hotel_factory, room_factory, booking_factory
):
    """Сортировка по hotel.id (возрастание)"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    hotels = hotel_factory(_quantity=3)
    hotels_sorted = sorted(hotels, key=lambda h: h.id)

    for h in hotels_sorted:
        room = room_factory(hotel=h)
        booking_factory(
            room=room,
            user=owner,
            start_date=_future_date(30),
            end_date=_future_date(31),
        )

    resp = api_client.get("/api/bookings/list/?order=hotel")
    assert resp.status_code == 200

    page = extract_page(resp)
    results = page["results"]

    extracted = [b["hotel"] for b in results]
    expected = [h.id for h in hotels_sorted]
    assert extracted == expected


def test_booking_sort_by_hotel_desc(
    api_client, hotel_factory, room_factory, booking_factory
):
    """Сортировка по hotel.id (убывание)"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    hotels = hotel_factory(_quantity=3)
    hotels_sorted_desc = sorted(hotels, key=lambda h: h.id, reverse=True)

    for h in hotels_sorted_desc:
        room = room_factory(hotel=h)
        booking_factory(
            room=room,
            user=owner,
            start_date=_future_date(40),
            end_date=_future_date(41),
        )

    resp = api_client.get("/api/bookings/list/?order=-hotel")
    assert resp.status_code == 200

    page = extract_page(resp)
    results = page["results"]

    extracted = [b["hotel"] for b in results]
    expected = [h.id for h in hotels_sorted_desc]
    assert extracted == expected


def test_booking_create(api_client, room_factory):
    """Создание бронирования — создаёт запись для текущего пользователя"""
    room = room_factory()

    payload = {
        "room_id": room.id,
        "start_date": _future_date(5),
        "end_date": _future_date(6),
    }

    resp = api_client.post("/api/bookings/create/", payload, format="json")
    assert resp.status_code == 201

    data = resp.json()
    assert data["room"] == room.id
    assert data["hotel"] == room.hotel.id
    assert data["booking_id"] > 0


def test_booking_delete(api_client, booking_factory):
    """Удаление бронирования — можно удалить только свою бронь"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    booking = booking_factory(user=owner)

    resp = api_client.delete(f"/api/bookings/delete/{booking.id}/")
    assert resp.status_code in (200, 204)

    resp_list = api_client.get("/api/bookings/list/")
    page = extract_page(resp_list)
    all_ids = [b["booking_id"] for b in page["results"]]
    assert booking.id not in all_ids


def test_booking_overlap_validation(api_client, room_factory):
    """Пересекающиеся даты — второе бронирование должно быть отклонено"""
    room = room_factory()

    payload1 = {
        "room_id": room.id,
        "start_date": _future_date(7),
        "end_date": _future_date(10),
    }
    resp1 = api_client.post("/api/bookings/create/", payload1, format="json")
    assert resp1.status_code == 201, resp1.json()

    payload2 = {
        "room_id": room.id,
        "start_date": _future_date(8),
        "end_date": _future_date(9),
    }
    resp2 = api_client.post("/api/bookings/create/", payload2, format="json")
    assert resp2.status_code == 400
    assert "Room is already booked for these dates" in str(resp2.data)


def test_booking_non_overlapping_success(api_client, room_factory):
    """Непересекающиеся даты — второе бронирование проходит"""
    room = room_factory()

    api_client.post(
        "/api/bookings/create/",
        {
            "room_id": room.id,
            "start_date": _future_date(1),
            "end_date": _future_date(2),
        },
        format="json",
    )

    resp = api_client.post(
        "/api/bookings/create/",
        {
            "room_id": room.id,
            "start_date": _future_date(10),
            "end_date": _future_date(11),
        },
        format="json",
    )
    assert resp.status_code == 201


def test_booking_invalid_room_id(api_client):
    """Если room_id не найден — возвращается ошибка с полем room_id"""
    payload = {
        "room_id": 999999,
        "start_date": _future_date(12),
        "end_date": _future_date(13),
    }
    resp = api_client.post("/api/bookings/create/", payload, format="json")
    assert resp.status_code == 400
    assert "room_id" in resp.data
    assert resp.data["room_id"][0] == "Room not found"


def test_booking_create_in_past_invalid(api_client, room_factory):
    """Создание брони в прошлом должно возвращать 400"""
    room = room_factory()

    payload = {
        "room_id": room.id,
        "start_date": (date.today() - timedelta(days=5)).isoformat(),
        "end_date": (date.today() - timedelta(days=3)).isoformat(),
    }

    resp = api_client.post("/api/bookings/create/", payload, format="json")
    assert resp.status_code == 400

    # У разных реализаций может быть 'start_date' или общий error
    body = resp.json()
    assert ("start_date" in body) or ("non_field_errors" in body)


def test_booking_filter_by_room(
    api_client, hotel_factory, room_factory, booking_factory
):
    """Фильтр: возвращаются только брони указанной комнаты"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    hotel = hotel_factory()
    room1 = room_factory(hotel=hotel)
    room2 = room_factory(hotel=hotel)

    b1 = booking_factory(room=room1, user=owner)
    booking_factory(room=room2, user=owner)

    resp = api_client.get(f"/api/bookings/list/?room_id={room1.id}")
    assert resp.status_code == 200

    page = extract_page(resp)
    results = page["results"]

    assert len(results) == 1
    assert results[0]["booking_id"] == b1.id


def test_booking_update_success(api_client, booking_factory):
    """Обновление бронирования — пользователь может изменить только свою бронь"""
    User = get_user_model()
    owner = User.objects.get(email="test@example.com")

    booking = booking_factory(user=owner)

    new_start = _future_date(20)
    new_end = _future_date(22)

    payload = {
        "room_id": booking.room.id,
        "start_date": new_start,
        "end_date": new_end,
    }

    resp = api_client.put(f"/api/bookings/update/{booking.id}/", payload, format="json")
    assert resp.status_code == 200

    data = resp.json()
    assert data["booking_id"] == booking.id
    assert data["start_date"] == new_start
    assert data["end_date"] == new_end
