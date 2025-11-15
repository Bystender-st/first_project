from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from booking.models.hotel import Hotel
from booking.serializers.hotel_serializers import HotelSerializer


class HotelCreateView(generics.CreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [AllowAny]


class HotelDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        hotel = get_object_or_404(Hotel, pk=pk)
        hotel.delete()
        return Response({"detail": "Hotel deleted"}, status=status.HTTP_200_OK)


class HotelListView(generics.ListAPIView):
    """
    Сортировка:
    - ?ordering=name — по имени (A → Z)
    - ?ordering=-name — по имени (Z → A)
    - ?ordering=created_at — по дате создания (старые первыми)
    - ?ordering=-created_at — по дате создания (новые первыми, по умолчанию)
    """

    queryset = Hotel.objects.all().order_by("-created_at")
    permission_classes = [AllowAny]
    serializer_class = HotelSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]
