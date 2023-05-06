from typing import Optional, List

from django.contrib.auth.hashers import check_password
from django.db import transaction

from api_user.models import Profile
from api_user.services import RoleService
from api_user.services.token import TokenService


class ProfileService:
    RANDOM_AVATARS = [
        "https://media-cdn.tripadvisor.com/media/photo-o/1a/f6/f0/48/default-avatar-2020-15.jpg",
        ""
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
    def create_dump_user_with_name(cls, reviewer_name: str):
        names = reviewer_name.split(" ", 1)
        if len(names) == 2:
            first_name, last_name = names
        else:
            first_name = names
            last_name = ""

