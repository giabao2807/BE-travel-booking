from django.db import connection
from django.db.models import QuerySet


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
        except ValueError:
            pass

        return int_value