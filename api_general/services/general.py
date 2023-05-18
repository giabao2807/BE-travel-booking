from api_hotel.serializers import HotelCardSerializer
from api_hotel.services import HotelService
from api_tour.models import Tour


class GeneralService:
    @classmethod
    def get_filter_query(cls, request):
        from api_tour.serializers import CardTourSerializer

        is_tour = request.query_params.get("is_tour", False)

        if is_tour:
            list_hotel_ids = HotelService.get_filter_query(request)
            hotel_cards = HotelService.get_hotel_cards(list_hotel_ids)
            data = HotelCardSerializer(hotel_cards, many=True).data
        else:
            tours = Tour.objects.all()
            data = CardTourSerializer(tours, many=True).data
        return data
