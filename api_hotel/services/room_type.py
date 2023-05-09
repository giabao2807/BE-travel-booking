from api_hotel.models import Hotel, RoomType


class RoomTypeService:
    @classmethod
    def get_room_type_ids_by_hotel(cls, hotel_id):
        hotel = Hotel.objects.get(id=hotel_id)
        room_types = RoomType.objects.filter(hotel=hotel)
        return [type.id for type in room_types]

    @classmethod
    def get_room_type_cards(cls, room_type_ids):
        room_type_cards = RoomType.objects.filter(id__in=room_type_ids)
        return room_type_cards
