from datetime import datetime

from django.db import connection
from django.db.models import QuerySet

from api_general.consts import DatetimeFormatter


class Utils:
    @classmethod
    def get_raw_query(cls, queryset: QuerySet) -> str:
        sql, params = queryset.query.sql_with_params()
        with connection.cursor() as cursor:
            cursor.execute('EXPLAIN ' + sql, params)
            raw_sql = cursor.db.ops.last_executed_query(cursor, sql, params)
        raw_sql = raw_sql[len('EXPLAIN '):]
        return raw_sql

    @classmethod
    def safe_int(cls, value, default_value: int = 0) -> int:
        int_value = default_value
        try:
            int_value = int(value)
        except Exception:
            pass

        return int_value

    @classmethod
    def safe_str_to_date(cls, date_str: str, datetime_formatter: str = DatetimeFormatter.YYMMDD, default_value=None) -> datetime:
        try:
            converted_datetime = datetime.strptime(date_str, datetime_formatter)
        except:
            converted_datetime = default_value

        return converted_datetime

    @classmethod
    def get_client_ip(cls, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
