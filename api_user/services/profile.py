from typing import Optional

from django.contrib.auth.hashers import check_password
from django.db import transaction

from api_user.models import Profile
from api_user.services import RoleService
from api_user.services.token import TokenService


class ProfileService:
    # @classmethod
    # @transaction.atomic
    # def create_customer(cls, user_data: dict) -> Optional[Profile]:
    #     """
    #     Create a new user with new account and default role
    #     :param user_data:
    #     :return:
    #     """
    #     user = None
    #     account = user_data.pop('account', {})
    #     if account:
    #         default_role = RoleService.get_role_customer()
    #         account_instance = AccountService.create(account, default_role)
    #         user_data['account'] = account_instance
    #         user = Profile(**user_data)
    #         user.save()
    #     return user

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
        - scopes
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
            'role': role.name
        }
        data = {**token_data, **user_data}
        return data
