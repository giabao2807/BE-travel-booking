from enum import Enum
from typing import List

from rest_framework import status
from rest_framework.exceptions import APIException


class ErrorType(Enum):
    GENERAL = (4001, "{0}")
    CANT_DEACTIVATE = (4002, "{0} can't be deactivated")
    CANT_ACTIVATE = (4003, "{0} can't be activated")
    CANT_CREATE = (4004, "{0} can't be created")
    EMPTY = (4005, "{0} can't be empty")
    INVALID = (4005, "{0} is invalid")
    AT_LEAST_ONE_FIELD = (4006, "must contain at least one of these fields: {0}")
    REQUIRED = (4007, "{0} is required")
    DEACTIVATED = (4008, "{0} is deactivated")

    # Custom for Vietnamese
    DEACTIVATED_VN = (4108, "{0} đã bị vô hiệu hóa")

    def __init__(self, code: int, error_message: str):
        self.code = code
        self.error_message = error_message


class BoniException(APIException):
    def __init__(self, error_type: ErrorType, params: List, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = error_type.error_message.format(*params)
        self.code = error_type.code
        self.status_code = status_code
