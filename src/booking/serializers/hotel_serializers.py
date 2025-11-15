from rest_framework import serializers

from booking.models import Hotel


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "address",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
