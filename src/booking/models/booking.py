from django.conf import settings
from django.db import models

from .room import Room


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        null=False,
        blank=False,
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.room} ({self.start_date} → {self.end_date})"
