from api_hotel.models import Hotel, Room


class RoomService:
    @classmethod
    def get_room_ids_by_hotel(cls, hotel_id):
        hotel = Hotel.objects.get(id=hotel_id)
        rooms = Room.objects.filter(hotel=hotel)
        return [type.id for type in rooms]

    @classmethod
    def get_room_cards(cls, room_ids):
        room_cards = Room.objects.filter(id__in=room_ids)
        return room_cards
