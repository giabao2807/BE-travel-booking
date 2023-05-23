from rest_framework.response import Response
from rest_framework.views import exception_handler

from base.exceptions import BoniException


def custom_exception_handler(exc, context):
    if isinstance(exc, BoniException):
        response_body = {
            "code": exc.code,
            "message": exc.message
        }
        return Response(response_body, status=exc.status_code)
    else:
        response = exception_handler(exc, context)
        return response
