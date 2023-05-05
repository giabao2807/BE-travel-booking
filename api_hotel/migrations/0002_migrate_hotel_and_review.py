# Generated by Django 4.1 on 2023-05-04 16:57
import json
import os
from typing import List

from django.db import migrations

from api_hotel.models import Hotel
from api_user.models import Profile
from api_user.services import ProfileService

default_cover_image = "https://ik.imagekit.io/tvlk/apr-asset/dgXfoyh24ryQLRcGq00cIdKHRmotrWLNlvG-TxlcLxGkiDwaUSggleJNPRgIHCX6/hotel/asset/20016842-3078abf5cf90a3ec8b59453f05737775.jpeg?_src=imagekit&tr=c-at_max,h-488,q-40,w-768"


special_city_mapping = {
    "Nha Trang": "Khánh Hoà",
    "Đà Lạt": "Lâm Đồng"
}


def initial_hotel_and_review_data(apps, schema_editor):
    hotel_model = apps.get_model("api_hotel", "Hotel")
    city_model = apps.get_model("api_general", "City")

    hotel_data_directory = "craw_data/all_hotel_data"
    failed_file_names: List[str] = []
    anonymous_users: List[Profile] = ProfileService.bulk_create_anonymous_users()
    current_city_name_mapping = dict(city_model.objects.all().values("name", "id"))

    all_files = os.listdir(hotel_data_directory)
    hotel_data_files = list(filter(lambda _file_name: _file_name.endswith(".json"), all_files))
    for _file_name in hotel_data_files:
        with open(f"{hotel_data_directory}/{_file_name}", "r", encoding='utf-8') as file:
            file_data: dict = json.loads(file.read())
            review_contents: List[dict] = file_data.get("content", [])
            hotel_data: dict = file_data.get("hotel", {})
            hotel_images: List[str] = hotel_data.get("images", [])
            cover_picture: str = hotel_images[0] if hotel_images else default_cover_image
            location_text: str = hotel_data.get("location", "")
            city_id: int = get_city_id_from_text(location_text, current_city_name_mapping)
            if not city_id:
                print(f"Fail with location text: {location_text}")
                failed_file_names.append(_file_name)
                continue

            hotel = hotel_model(
                name=hotel_data.get("name", ""),
                cover_picture=cover_picture,
                address=location_text,
                city_id=city_id,
                longitude=hotel_data.get("geo_data", {}).get("longitude", 0),
                latitude=hotel_data.get("geo_data", {}).get("latitude", 0),
                room_size=int(hotel_data.get("room_number", "0"))
            )
            hotel.save()

    print("Failed file: ", failed_file_names)


def get_city_id_from_text(location_text: str, current_city_name_mapping: dict[str, int]) -> int:
    city_id = 0
    for _city_name, _city_id in current_city_name_mapping.items():
        if _city_name in location_text:
            city_id = _city_id
            break

    if not city_id:
        correct_city_name: str = ""
        for _special_city_name, _correct_city_name in special_city_mapping.items():
            if _special_city_name in location_text:
                correct_city_name = _correct_city_name
                break
        if correct_city_name:
            city_id = current_city_name_mapping.get(correct_city_name)

    return city_id


def saving_hotel_reviews(hotel: Hotel, review_contents: List[dict]):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api_hotel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_hotel_and_review_data, migrations.RunPython.noop)
    ]
