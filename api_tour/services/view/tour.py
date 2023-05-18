from datetime import datetime
from typing import Optional, Tuple

from rest_framework.exceptions import ValidationError

from api_general.services import Utils


class TourViewService:
    @classmethod
    def validate_filter_by_date_params(cls, start_date: str, end_date: str) -> Tuple[datetime, datetime]:
        """
        Pre-check params for filter_by_date API
        Raise Validation Error immediately -> return 400 status + message
        @param start_date: (str) Must have valid value with format (YYYY-MM-DD)
        @param end_date: (str) Must have valid value with format (YYYY-MM-DD)
        @return: converted start and end date
        """
        converted_start_date: Optional[datetime] = Utils.safe_str_to_date(start_date)
        converted_end_date: Optional[datetime] = Utils.safe_str_to_date(end_date)

        if not converted_start_date:
            raise ValidationError("start_date field is invalid!")
        if not converted_end_date:
            raise ValidationError("end_date field is invalid!")
        if converted_start_date > converted_end_date:
            raise ValidationError("start_date must be greater than end_date!")

        return converted_start_date, converted_end_date
