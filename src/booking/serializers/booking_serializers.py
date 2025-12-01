from datetime import date

from django.db.models import Q
from rest_framework import serializers

from booking.models import Booking, Room


class BookingSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(write_only=True)
    room = serializers.IntegerField(source="room.id", read_only=True)
    hotel = serializers.IntegerField(source="room.hotel.id", read_only=True)
    booking_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "hotel",
            "room",
            "room_id",
            "start_date",
            "end_date",
        ]
        read_only_fields = ["booking_id", "hotel", "room"]

    def validate(self, data):
        start = data["start_date"]
        end = data["end_date"]
        room_id = data["room_id"]

        if start < date.today():
            raise serializers.ValidationError("Cannot book a past date.")

        if end <= start:
            raise serializers.ValidationError("end_date must be after start_date")

        if not Room.objects.filter(pk=room_id).exists():
            raise serializers.ValidationError({"room_id": "Room not found"})

        overlapping = Booking.objects.filter(room_id=room_id).filter(
            Q(start_date__lt=end) & Q(end_date__gt=start)
        )

        instance = getattr(self, "instance", None)
        if instance:
            overlapping = overlapping.exclude(pk=instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError("Room is already booked for these dates")

        return data

    def create(self, validated_data):
        room = Room.objects.get(pk=validated_data.pop("room_id"))
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")

        user = request.user

        return Booking.objects.create(room=room, user=user, **validated_data)

    def update(self, instance, validated_data):
        room = Room.objects.get(pk=validated_data.pop("room_id", instance.room.id))
        instance.room = room
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.end_date = validated_data.get("end_date", instance.end_date)
        instance.save()
        return instance
