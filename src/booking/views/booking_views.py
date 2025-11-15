from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from booking.models.booking import Booking
from booking.serializers.booking_serializers import BookingSerializer


class BookingListView(generics.ListAPIView):
    """
    Список броней с фильтрацией по hotel_id, room_id
    и сортировкой по дате начала (asc/desc).
    """

    permission_classes = [AllowAny]
    serializer_class = BookingSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "room_id",
                openapi.IN_QUERY,
                description="Фильтрация по ID комнаты",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "hotel_id",
                openapi.IN_QUERY,
                description="Фильтрация по ID отеля",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "order",
                openapi.IN_QUERY,
                description="Порядок сортировки по дате начала",
                type=openapi.TYPE_STRING,
                enum=["asc", "desc"],
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Booking.objects.all()

        room_id = self.request.query_params.get("room_id")
        hotel_id = self.request.query_params.get("hotel_id")
        order = self.request.query_params.get("order", "asc")

        if room_id:
            qs = qs.filter(room_id=room_id)
        if hotel_id:
            qs = qs.filter(room__hotel_id=hotel_id)

        qs = qs.order_by("-start_date" if order == "desc" else "start_date")

        return qs


class BookingCreateView(generics.CreateAPIView):
    """
    Создание брони (room_id, start_date, end_date)
    """

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=BookingSerializer,
        responses={201: BookingSerializer},
        operation_description="Создание новой брони",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BookingDeleteView(APIView):
    """
    Удаление брони по ID
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: "Booking deleted"},
        operation_description="Удаление бронирования по ID",
    )
    def delete(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return Response({"detail": "Booking deleted"}, status=status.HTTP_200_OK)
