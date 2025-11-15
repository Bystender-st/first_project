from django.urls import path

from booking.views.booking_views import (
    BookingCreateView,
    BookingDeleteView,
    BookingListView,
)
from booking.views.hotel_views import HotelCreateView, HotelDeleteView, HotelListView
from booking.views.room_views import RoomCreateView, RoomDeleteView, RoomListView

urlpatterns = [
    # Hotels
    path("hotels/create/", HotelCreateView.as_view(), name="hotel-create"),
    path("hotels/<int:pk>/delete/", HotelDeleteView.as_view(), name="hotel-delete"),
    path("hotels/list/", HotelListView.as_view(), name="hotel-list"),
    # Rooms
    path("rooms/create/", RoomCreateView.as_view(), name="room-create"),
    path("rooms/delete/<int:pk>/", RoomDeleteView.as_view(), name="room-delete"),
    path("rooms/list/", RoomListView.as_view(), name="room-list"),
    # Bookings
    path("bookings/create/", BookingCreateView.as_view(), name="booking-create"),
    path(
        "bookings/delete/<int:pk>/", BookingDeleteView.as_view(), name="booking-delete"
    ),
    path("bookings/list/", BookingListView.as_view(), name="booking-list"),
]
