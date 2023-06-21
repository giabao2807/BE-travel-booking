from api_booking.models import Booking
from api_hotel.models import Hotel, Room, RoomImage
from common.constants.api_booking import BookingStatus


class RoomService:
    @classmethod
    def check_delete_room(cls, room):
        is_valid = True
        bookings = Booking.objects.filter(booking_item__room=room, status__in=[BookingStatus.PAID, BookingStatus.UNPAID])
        if bookings:
            return False
        return is_valid

    @classmethod
    def get_room_ids_by_hotel(cls, hotel_id):
        hotel = Hotel.objects.get(id=hotel_id)
        rooms = Room.objects.filter(hotel=hotel)
        return [type.id for type in rooms]

    @classmethod
    def get_room_cards(cls, room_ids):
        room_cards = Room.objects.filter(id__in=room_ids)
        return room_cards

    @classmethod
    def bulk_create_room_images(cls, room_images: list, room_id):
        from api_general.services import ImageService

        ImageService.bulk_create_related_model_images(room_images, RoomImage, "room_id", room_id)
