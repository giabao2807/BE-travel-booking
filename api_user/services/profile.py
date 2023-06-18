import os
import random
import string
from typing import Optional, List

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.db.models import CharField, Value
from django.db.models.functions import Collate, Concat
from django.template.loader import render_to_string

from api_user.models import Profile, Role
from api_user.services import RoleService
from api_user.services.token import TokenService
from api_user.statics import RoleData
from dotenv import load_dotenv

from base.services.send_mail import SendMail
from base.utils import Utils

load_dotenv()


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
    def list_partner(cls):
        partner_role_id = RoleData.PARTNER.id
        queryset = Profile.objects.filter(role__id=partner_role_id)
        return queryset

    @classmethod
    def get_filter_query(cls, request):
        queryset = Profile.objects.all()
        filter_args = dict()
        name = request.query_params.get("name", "")
        role = request.query_params.get("role", None)

        if role:
            filter_args.update(role__id=role)
        if name:
            name = Collate(Value(name.strip()), "utf8mb4_general_ci")

        queryset = queryset.annotate(full_name=Concat('last_name', Value(' '), 'first_name', output_field=CharField())) \
            .filter(full_name__icontains=name, **filter_args)
        return queryset

    @classmethod
    @transaction.atomic
    def create_customer(cls, user_data: dict) -> Optional[Profile]:
        """
        Create a new user with new account and default role
        :param user_data:
        :return:
        """
        default_role = RoleService.get_role_customer()
        password = user_data.pop('password')
        user_data['password'] = make_password(password,
                                              os.getenv('DEFAULT_PASSWORD'))
        user = Profile(**user_data)
        user.role = default_role
        user.save()
        cls.send_mail(email=user.email, name=f'{user.first_name} {user.last_name}',
                      send_email=True, password=password, base_link=os.getenv('FE_BASE_LINK'))
        return user

    @classmethod
    @transaction.atomic
    def create_partner(cls, user_data: dict) -> Optional[Profile]:
        """
        Create a new user with new account and default role
        :param user_data:
        :return:
        """
        default_role = RoleService.get_role_partner()
        password = Utils.gen_password()
        user_data['password'] = make_password(password,
                                              os.getenv('DEFAULT_PASSWORD'))
        user = Profile(**user_data)
        user.role = default_role
        user.save()
        cls.send_mail(email=user.email, name=f'{user.first_name} {user.last_name}',
                      send_email=True, password=password, base_link=os.getenv('FE_BASE_LINK'))
        return user

    @classmethod
    def send_mail(cls,
                  email,
                  name,
                  password,
                  send_email=False,
                  base_link=""):
        if send_email:
            # TODO: Look at the link again
            link = f"{base_link}"
            content = render_to_string(
                "invite_email.html",
                {"name": name, "email": email, "password": password, "link": link},
            )
            SendMail.start(
                [email], "Welcome to Boni Travel", content
            )

    @classmethod
    def send_mail_reset_password(
            cls,
            email=None,
            phone=None,
            personal_email=None,
            send_email=False,
            base_link=os.getenv('FE_BASE_LINK'),
            password="",
    ):
        if send_email:
            link = f"{base_link}"
            content = render_to_string(
                "reset_password.html",
                {"email": email, "password": password, "link": link},
            )
            SendMail.start(
                [email, personal_email], "[RESET PASSWORD] New generator password for your account", content
            )

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
            'phone': profile.phone,
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
