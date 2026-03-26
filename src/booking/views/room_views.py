from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from booking.models.room import Room
from booking.serializers.room_serializers import RoomSerializer


class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]


class RoomDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        return Response({"detail": "Room deleted"}, status=status.HTTP_200_OK)


class RoomListView(generics.ListAPIView):
    """
    Сортировка доступна по:
      - цене(от меньшего к большему): ?ordering=price_per_night
      - цене(от большего к меньшему): ?ordering=-price_per_night
      - дате создания(старые первыми): ?ordering=created_at
      - дате создания(новые первыми, по умолчанию):?ordering=-created_at
    """

    queryset = Room.objects.all().order_by("-created_at")
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "price_per_night"]
    ordering = ["-created_at"]
