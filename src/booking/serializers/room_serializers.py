from rest_framework import serializers

from booking.models import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "hotel",
            "number",
            "capacity",
            "price_per_night",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
