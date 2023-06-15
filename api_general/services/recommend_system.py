import requests

from api_user.models import Profile

API_RECOMMEND_URL = 'https://6a25-14-241-121-188.ngrok-free.app'


class RecommendService:
    @classmethod
    def get_recommend_top_tour(cls, num: int):
        number = num or 6
        response = requests.get(f'{API_RECOMMEND_URL}/tour/top-tour?limit={number}')
        recommend_tours = response.json().get("data")
        tour_ids = [tour.get("tour_id") for tour in recommend_tours]
        return tour_ids

    @classmethod
    def get_recommend_tour_for_user(cls, user: Profile, num: int):
        number = num or 6
        response = requests.get(f'{API_RECOMMEND_URL}/user/{user.id.hex}/recommend-tour?limit={number}')
        recommend_tours = response.json().get("data")
        tour_ids = [tour.get("id") for tour in recommend_tours]
        return tour_ids

    @classmethod
    def get_recommend_hotel_for_user(cls, user: Profile, num: int):
        number = num or 6
        response = requests.get(f'{API_RECOMMEND_URL}/user/{user.id.hex}/recommend-hotel?limit={number}')
        recommend_hotels = response.json().get("data")
        hotel_ids = [hotel.get("id") for hotel in recommend_hotels]
        return hotel_ids

    @classmethod
    def get_recommend_top_city(cls):
        response = requests.get(f'{API_RECOMMEND_URL}/city/top-city')
        recommend_cities = response.json().get("data")
        city_ids = [city.get("id") for city in recommend_cities]
        return city_ids
