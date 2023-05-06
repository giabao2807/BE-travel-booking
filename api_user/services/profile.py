import os
import random
import string
from typing import Optional, List

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction

from api_user.models import Profile, Role
from api_user.services import RoleService
from api_user.services.token import TokenService
from api_user.statics import RoleData


class ProfileService:
    RANDOM_AVATARS = [
        "https://media-cdn.tripadvisor.com/media/photo-o/1a/f6/f0/48/default-avatar-2020-15.jpg",
        ""
    ]
    DUMP_FIRST_NAMES = {
        Profile.GenderChoices.MALE: [
            "Huy",
            "Khang",
            "Bảo",
            "Minh",
            "Phúc",
            "Anh",
            "Khoa",
            "Phát",
            "Đạt",
            "Khôi",
            "Long",
            "Nam",
            "Duy",
            "Quân",
            "Kiệt",
            "Thịnh",
            "Tuấn",
            "Hưng",
            "Hoàng",
            "Hiếu",
        ],
        Profile.GenderChoices.FEMALE: [
            "Anh",
            "Trang",
            "Linh",
            "Phương",
            "Hương",
            "Thảo",
            "Hà",
            "Huyền",
            "Ngọc",
            "Hằng",
            "Giang",
            "Nhung",
            "Yến",
            "Nga",
            "Mai",
            "Thu",
            "Hạnh",
            "Vân",
            "Hoa",
            "Hiền",
        ]
    }
    DUMP_LAST_NAMES = [
        "Nguyễn",
        "Trần",
        "Lê",
        "Phạm",
        "Hoàng/Huỳnh",
        "Phan",
        "Vũ/Võ",
        "Đặng",
        "Bùi",
        "Đỗ",
        "Hồ",
        "Ngô",
        "Dương",
        "Lý"
    ]
    @classmethod
    @transaction.atomic
    def create_customer(cls, user_data: dict) -> Optional[Profile]:
        """
        Create a new user with new account and default role
        :param user_data:
        :return:
        """
        default_role = RoleService.get_role_customer()
        user = Profile(**user_data)
        user.role = default_role
        user.save()
        return user

    @classmethod
    def login(cls, login_data) -> Optional[dict]:
        """
        Verify login data
        :param login_data:
        - email
        - password
        :return:
        general information if valid data
        else None
        """
        from api_user.services import ProfileService

        response_data = None
        email = login_data.get('email', "")
        password = login_data.get('password', "")
        profile = Profile.objects.by_email(email)
        if profile and check_password(password, profile.password):
            response_data = ProfileService.login_success_data(profile)
        return response_data

    @classmethod
    def login_success_data(cls, profile: Profile):
        """
        Return success data for login
        :param profile:
        :return: dictionary data with general user information and token
        included fields:
        - id
        - name
        - avatar
        - access_token
        - refresh_token
        """
        token_data = TokenService.generate_by_account(profile)
        role = profile.role
        user_data = {
            'id': profile.id,
            'full_name': f"{profile.first_name} {profile.last_name}",
            'avatar': profile.avatar,
            'email': profile.email,
            'role': role.name
        }
        data = {**token_data, **user_data}
        return data

    @classmethod
    def bulk_create_anonymous_users(cls) -> List[Profile]:
        pass

    @classmethod
    def create_dump_user_with_name(cls, reviewer_name: str, role: RoleData, address: str = ""):
        names = reviewer_name.split(" ", 1)
        if len(names) == 2:
            first_name, last_name = names
        else:
            first_name = names
            last_name = ""

        random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        avatar = random.choice(cls.RANDOM_AVATARS)
        role = Role.objects.filter(name=role.value.get("name")).first()
        email = f"bookingtravel_{first_name}_{random_str}@gmail.com"
        user = Profile(
            first_name=first_name,
            last_name=last_name,
            email=email,
            avatar=avatar,
            password=make_password(os.getenv('DEFAULT_PASSWORD')),
            role=role,
            gender=random.choice(Profile.GenderChoices.choices)[0],
            address=address
        )
        user.save()

        return user

    @classmethod
    def random_name(cls) -> str:
        gender = random.choice([Profile.GenderChoices.MALE, Profile.GenderChoices.FEMALE])
        last_name = random.choice(cls.DUMP_LAST_NAMES)
        first_name = random.choice(cls.DUMP_FIRST_NAMES.get(gender))

        return f"{first_name} {last_name}"
