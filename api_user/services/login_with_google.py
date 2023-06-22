import os

from dotenv import load_dotenv

from api_user.models import Profile
from api_user.services import ProfileService, TokenService
from base.exceptions import BoniException
from base.exceptions.base import ErrorType

load_dotenv()
from google.oauth2 import id_token
from google.auth.transport import requests


class GoogleLoginService:
    @staticmethod
    def login(info: dict):
        """
        Login with Google account, auto create a new account with random password if email does not exist
        :param info: (dict) result data after verify with token ID given from FE
        must contain:
        email
        given_name
        family_name
        :return: dict
        contains: access_token & refresh_token
        """
        email = info.get('email', '')
        first_name = info.get('family_name', '')
        last_name = info.get('given_name', '')
        avatar = info.get('picture', '')


        profile = Profile.objects.filter(email=email).first()
        if not profile:
            profile_data = dict(
                email=email,
                first_name=first_name,
                last_name=last_name,
                gender=Profile.GenderChoices.OTHER,
                avatar=avatar,
                password=os.getenv("DEFAULT_PASSWORD", "12341234")
            )
            profile = ProfileService.create_customer(profile_data)

        return ProfileService.success_response_for_login(profile)

    @staticmethod
    def verify_google_token_id(token: str):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        user_info = dict()

        if not token:
            raise BoniException(ErrorType.EMPTY, ['token'])
        try:
            user_info = id_token.verify_oauth2_token(token, requests.Request(), client_id, clock_skew_in_seconds=100)
        except Exception as e:
            print(e)

        return user_info
