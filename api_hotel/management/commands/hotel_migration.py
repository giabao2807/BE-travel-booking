import json
import os
import random
from typing import List, Type

from django.core.management import BaseCommand
from django.db import transaction
from unidecode import unidecode

from api_general.models import City, Image
from api_hotel.models import Hotel, HotelImage, RoomImage, Room
from api_hotel.models.review import HotelReview
from api_user.models import Profile
from api_user.services import ProfileService
from api_user.statics import RoleData


class Command(BaseCommand):
    help = "Migrate hotel data"

    def add_arguments(self, parser):
        parser.add_argument("--migrate_hotel_and_reviews_data",
                            action="store_true",
                            help="Migrate hotel and reviews from crawled data", )
        parser.add_argument("--migrate_hotel_images_data",
                            action="store_true",
                            help="Migrate hotel images from crawled data", )
        parser.add_argument("--migrate_roomtype_room",
                            action="store_true",
                            help="Migrate room_type room for hotel from crawled data", )

    def handle(self, *args, **options):
        if options.get("migrate_hotel_and_reviews_data"):
            self.initial_hotel_and_review_data()
        if options.get("migrate_hotel_images_data"):
            self.migrate_hotel_images_data()
        if options.get("migrate_roomtype_room"):
            self.migrate_room_type_room()

    default_cover_image = "https://ik.imagekit.io/tvlk/apr-asset/dgXfoyh24ryQLRcGq00cIdKHRmotrWLNlvG-TxlcLxGkiDwaUSggleJNPRgIHCX6/hotel/asset/20016842-3078abf5cf90a3ec8b59453f05737775.jpeg?_src=imagekit&tr=c-at_max,h-488,q-40,w-768"

    special_city_mapping = {
        "Nha Trang": "Khánh Hoà",
        "Đà Lạt": "Lâm Đồng",
        "Phú Quốc": "Kiên Giang",
        "Phan Rang": "Ninh Thuận",
        "Cam Ranh": "Khánh Hòa",
        "Ho Chi Minh": "Tp. Hồ Chí Minh",
        "Hanoi": "Hà Nội"
    }

    @transaction.atomic
    def initial_hotel_and_review_data(self):
        hotel_model = Hotel
        city_model = City
        hotel_review_model = HotelReview

        hotel_data_directory = "craw_data/all_hotel_data"
        failed_file_names: List[str] = []
        current_city_name_mapping = dict(city_model.objects.all().values_list("name", "id"))

        all_files = os.listdir(hotel_data_directory)
        hotel_data_files = list(filter(lambda _file_name: _file_name.endswith(".json"), all_files))
        for _idx, _file_name in enumerate(hotel_data_files):
            with open(f"{hotel_data_directory}/{_file_name}", "r", encoding='utf-8') as file:
                file_data: dict = json.loads(file.read())
                review_contents: List[dict] = file_data.get("content", [])
                hotel_data: dict = file_data.get("hotel", {})
                hotel_name: str = hotel_data.get("name", "")
                hotel_images: List[str] = hotel_data.get("images", [])
                cover_picture: str = hotel_images[0] if hotel_images else self.default_cover_image
                location_text: str = hotel_data.get("location", "")
                city_id: int = self.get_city_id_from_text(_file_name, current_city_name_mapping)
                if not city_id:
                    print(f"Fail with location text: {location_text}")
                    failed_file_names.append(_file_name)
                    continue

                random_name = ProfileService.random_name()
                owner = ProfileService.create_dump_user_with_name(random_name, RoleData.PARTNER)

                hotel = hotel_model(
                    name=hotel_name,
                    cover_picture=cover_picture,
                    address=location_text,
                    city_id=city_id,
                    longitude=hotel_data.get("geo_data", {}).get("longitude", 0),
                    latitude=hotel_data.get("geo_data", {}).get("latitude", 0),
                    owner_id=owner.id
                )
                hotel.save()
                self.saving_hotel_reviews(hotel_review_model, hotel, review_contents)

                print(
                    f">>> Done [{_idx}/{len(hotel_data_files)}] with hotel: {hotel_name} and {len(review_contents)} reviews")

        print("Failed file: ", failed_file_names)

    def get_city_id_from_text(self, location_text: str, current_city_name_mapping: dict[str, int]) -> int:
        city_id = 0
        location_text = location_text.replace("_", " ")
        for _city_name, _city_id in current_city_name_mapping.items():
            _decoded_city_name = unidecode(_city_name)
            if _city_name in location_text or _decoded_city_name in location_text:
                city_id = _city_id
                break

        if not city_id:
            correct_city_name: str = ""
            for _special_city_name, _correct_city_name in self.special_city_mapping.items():
                _decoded_special_city_name = unidecode(_special_city_name)
                if _special_city_name in location_text or _decoded_special_city_name in location_text:
                    correct_city_name = _correct_city_name
                    break
            if correct_city_name:
                city_id = current_city_name_mapping.get(correct_city_name)

        return city_id

    def saving_hotel_reviews(self, hotel_review_model: Type[HotelReview], hotel: Hotel, review_contents: List[dict]):
        hotel_reviews: List[HotelReview] = []

        for _review in review_contents:
            reviewer_location = _review.get("reviewer_location", "")
            reviewer_name = _review.get("name", "")

            if reviewer_location == "dumpxxx":
                reviewer_location = ""
            reviewer: Profile = ProfileService.create_dump_user_with_name(reviewer_name, RoleData.CUSTOMER,
                                                                          reviewer_location)

            hotel_reviews.append(
                hotel_review_model(
                    hotel=hotel,
                    title=_review.get("review_title", ""),
                    content=_review.get("review_content", ""),
                    rate=_review.get("review_rating", 0),
                    owner_id=reviewer.id
                )
            )

        hotel_review_model.objects.bulk_create(hotel_reviews)

    def migrate_hotel_images_data(self):
        hotel_data_directory = "craw_data/all_hotel_data"
        failed_file_names: List[str] = []
        bulk_hotel_images: List[HotelImage] = []

        all_files = os.listdir(hotel_data_directory)
        hotel_data_files = list(filter(lambda _file_name: _file_name.endswith(".json"), all_files))
        for _idx, _file_name in enumerate(hotel_data_files):
            print(f"[{_idx + 1}/{len(hotel_data_files)}] Fetching hotel images: {_file_name}")
            with open(f"{hotel_data_directory}/{_file_name}", "r", encoding='utf-8') as file:
                file_data: dict = json.loads(file.read())
                hotel_data: dict = file_data.get("hotel", {})
                hotel_name: str = hotel_data.get("name", "")
                hotel_images: List[str] = hotel_data.get("images", [])
                bulk_images: List[Image] = []

                if not hotel_name or not hotel_images:
                    continue

                hotel = Hotel.objects.filter(name=hotel_name).first()

                if all([hotel_name, hotel, hotel_images]):

                    for _image_url in hotel_images:
                        bulk_images.append(
                            Image(
                                link=_image_url
                            )
                        )
                    Image.objects.bulk_create(bulk_images)
                    created_images: List[Image] = Image.objects.filter(link__in=hotel_images)
                    for _image in created_images:
                        bulk_hotel_images.append(
                            HotelImage(
                                hotel_id=hotel.id,
                                image_id=_image.id
                            )
                        )
                else:
                    failed_file_names.append(_file_name)
                print(f">>> Fetched {len(bulk_images)} hotel images: {_file_name}")
        print(f"Bulk creating {len(bulk_hotel_images)} HotelImage records ...")
        HotelImage.objects.bulk_create(bulk_hotel_images)
        print("Done!")
        print("Failed with file names: ", failed_file_names)


    def migrate_room_type_room(self):
        room_model = Room
        room_image_model = RoomImage
        image_model = Image
        hotel_model = Hotel

        # delete room and room image existed
        room_model.objects.all().delete()
        room_image_model.objects.all().delete()
        hotels = hotel_model.objects.all()

        with open('api_hotel/statics/room_type.txt', 'r', encoding='utf-8') as f:
            list_data = json.load(f)

        len_room_type = len(list_data)

        for idx, hotel in enumerate(hotels):
            print("Migrate roomtype for hotel: ", idx, hotel.name)
            random_room_types = list_data[str(random.randint(0, len_room_type - 1))]

            for room_type in random_room_types:
                room_instance = room_model(name=room_type['name'], beds=room_type['beds'],
                                           adults=int(room_type['adults']), children=int(room_type['children']),
                                           description=room_type['description'], square=room_type['square'],
                                           price=int(room_type['price']), hotel=hotel, quantity=random.randint(5, 10))
                list_room_type_image = []
                room_instance.save()
                for image in room_type['images']:
                    image_instance = image_model(link=image)
                    image_instance.save()
                    room_type_image = room_image_model(image=image_instance, room=room_instance)
                    list_room_type_image.append(room_type_image)
                room_image_model.objects.bulk_create(list_room_type_image)
            print("------Done\n")

    #
    # def migrate_room_type_room(self):
    #     room_type_model = RoomType
    #     room_model = Room
    #     room_type_image_model = RoomTypeImage
    #     image_model = Image
    #     hotel_model = Hotel
    #     hotels = hotel_model.objects.all()
    #
    #     with open('api_hotel/statics/room_type.txt', 'r', encoding='utf-8') as f:
    #         list_data = json.load(f)
    #
    #     len_room_type = len(list_data)
    #
    #     for idx, hotel in enumerate(hotels):
    #         print("Migrate for hotel: ", idx)
    #         random_room_types = list_data[str(random.randint(0, len_room_type - 1))]
    #
    #         for room_type in random_room_types:
    #             room_type_instance = room_type_model(name=room_type['name'], beds=room_type['beds'],
    #                                                  adults=int(room_type['adults']),
    #                                                  children=int(room_type['children']),
    #                                                  description=room_type['description'], square=room_type['square'],
    #                                                  price=int(room_type['price']), hotel=hotel)
    #             list_room_type_image = []
    #             room_type_instance.save()
    #             for image in room_type['images']:
    #                 image_instance = image_model(link=image)
    #                 image_instance.save()
    #                 room_type_image = room_type_image_model(image=image_instance, room_type=room_type_instance)
    #                 list_room_type_image.append(room_type_image)
    #             room_type_image_model.objects.bulk_create(list_room_type_image)
    #
    #             random_room_for_room_type = random.randint(1, 8)
    #             for i in range(1, random_room_for_room_type + 1):
    #                 room = room_model(room_type=room_type_instance)
    #                 room.save()
    #         print("------Done\n")
