from model_bakery import baker


class HotelFactory:
    @staticmethod
    def create(**kwargs):
        return baker.make("booking.Hotel", **kwargs)


class RoomFactory:
    @staticmethod
    def create(**kwargs):
        # чтобы не ломалось, если не передали hotel
        if "hotel" not in kwargs:
            kwargs["hotel"] = baker.make("booking.Hotel")
        return baker.make("booking.Room", **kwargs)


class BookingFactory:
    @staticmethod
    def create(**kwargs):
        if "room" not in kwargs:
            kwargs["room"] = baker.make("booking.Room")
        return baker.make("booking.Booking", **kwargs)
