import pytest

pytestmark = pytest.mark.django_db


def test_booking_list_empty(api_client):
    """Если бронирований нет — возвращается пустой список"""
    resp = api_client.get("/api/bookings/list/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_booking_list_multiple(api_client, booking_factory):
    """Создаем несколько бронирований и проверяем, что они возвращаются"""
    bookings = booking_factory(_quantity=5)

    resp = api_client.get("/api/bookings/list/")
    data = resp.json()

    assert resp.status_code == 200
    assert len(data) == 5

    returned_ids = {b["booking_id"] for b in data}
    expected_ids = {b.id for b in bookings}

    assert returned_ids == expected_ids


def test_booking_filter_by_hotel(
    api_client, hotel_factory, room_factory, booking_factory
):
    """Фильтр: должен вернуть бронирования только указанного отеля"""
    hotel1 = hotel_factory()
    hotel2 = hotel_factory()

    room1 = room_factory(hotel=hotel1)
    room2 = room_factory(hotel=hotel2)

    b1 = booking_factory(room=room1)
    booking_factory(room=room2)

    resp = api_client.get(f"/api/bookings/list/?hotel_id={hotel1.id}")
    data = resp.json()

    assert len(data) == 1
    assert data[0]["booking_id"] == b1.id


def test_booking_sort_by_room_asc(api_client, room_factory, booking_factory):
    """Сортировка по номеру комнаты: по возрастанию"""
    rooms = room_factory(_quantity=3)
    rooms_sorted = sorted(rooms, key=lambda r: r.id)

    for r in rooms_sorted:
        booking_factory(room=r)

    resp = api_client.get("/api/bookings/list/?ordering=room")
    data = resp.json()

    extracted = [b["room"] for b in data]
    expected = [r.id for r in rooms_sorted]

    assert extracted == expected


def test_booking_sort_by_room_desc(api_client, room_factory, booking_factory):
    """Сортировка по номеру комнаты: по убыванию"""
    rooms = room_factory(_quantity=3)
    rooms_sorted_desc = sorted(rooms, key=lambda r: r.id, reverse=True)

    for r in rooms_sorted_desc:
        booking_factory(room=r)

    resp = api_client.get("/api/bookings/list/?ordering=-room")
    data = resp.json()

    extracted = [b["room"] for b in data]
    expected = [r.id for r in rooms_sorted_desc]

    assert extracted == expected


def test_booking_sort_by_hotel_asc(
    api_client, hotel_factory, room_factory, booking_factory
):
    """Сортировка по отелю: по возрастанию"""
    hotels = hotel_factory(_quantity=3)
    hotels_sorted = sorted(hotels, key=lambda h: h.id)

    for h in hotels_sorted:
        room = room_factory(hotel=h)
        booking_factory(room=room)

    resp = api_client.get("/api/bookings/list/?ordering=hotel")
    data = resp.json()

    extracted = [b["hotel"] for b in data]
    expected = [h.id for h in hotels_sorted]

    assert extracted == expected


def test_booking_sort_by_hotel_desc(
    api_client, hotel_factory, room_factory, booking_factory
):
    """Сортировка по отелю: по убыванию"""
    hotels = hotel_factory(_quantity=3)
    hotels_sorted_desc = sorted(hotels, key=lambda h: h.id, reverse=True)

    for h in hotels_sorted_desc:
        room = room_factory(hotel=h)
        booking_factory(room=room)

    resp = api_client.get("/api/bookings/list/?ordering=-hotel")
    data = resp.json()

    extracted = [b["hotel"] for b in data]
    expected = [h.id for h in hotels_sorted_desc]

    assert extracted == expected


def test_booking_create(api_client, room_factory):
    """Создание бронирования"""
    room = room_factory()

    payload = {
        "room_id": room.id,
        "start_date": "2025-05-10",
        "end_date": "2025-05-12",
    }

    resp = api_client.post("/api/bookings/create/", payload, format="json")

    assert resp.status_code == 201
    data = resp.json()

    assert data["room"] == room.id
    assert data["hotel"] == room.hotel.id
    assert data["booking_id"] > 0


def test_booking_delete(api_client, booking_factory):
    """Удаление бронирования"""
    booking = booking_factory()

    resp = api_client.delete(f"/api/bookings/delete/{booking.id}/")
    assert resp.status_code in (200, 204)

    resp_list = api_client.get("/api/bookings/list/")
    all_ids = [b["id"] for b in resp_list.json()]

    assert booking.id not in all_ids


def test_booking_overlap_validation(api_client, room_factory):
    """Второе бронирование с пересечением дат недопустимо."""
    room = room_factory()

    payload1 = {
        "room_id": room.id,
        "start_date": "2025-05-10",
        "end_date": "2025-05-15",
    }

    resp1 = api_client.post("/api/bookings/create/", payload1, format="json")

    assert resp1.status_code == 201, resp1.json()

    payload2 = {
        "room_id": room.id,
        "start_date": "2025-05-12",
        "end_date": "2025-05-14",
    }

    resp2 = api_client.post("/api/bookings/create/", payload2, format="json")

    assert resp2.status_code == 400
    assert "Room is already booked for these dates" in str(resp2.data)


def test_booking_non_overlapping_success(api_client, room_factory):
    """Второе бронирование допустимо."""
    room = room_factory()

    api_client.post(
        "/api/bookings/create/",
        {
            "room_id": room.id,
            "start_date": "2025-05-01",
            "end_date": "2025-05-05",
        },
        format="json",
    )

    resp = api_client.post(
        "/api/bookings/create/",
        {
            "room_id": room.id,
            "start_date": "2025-05-10",
            "end_date": "2025-05-12",
        },
        format="json",
    )

    assert resp.status_code == 201


def test_booking_invalid_room_id(api_client):
    """Проверка 'Room not found'."""

    payload = {
        "room_id": 999999,
        "start_date": "2025-06-01",
        "end_date": "2025-06-05",
    }

    resp = api_client.post("/api/bookings/create/", payload, format="json")

    assert resp.status_code == 400
    assert "room_id" in resp.data
    assert resp.data["room_id"][0] == "Room not found"
