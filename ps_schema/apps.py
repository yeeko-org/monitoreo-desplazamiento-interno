from django.apps import AppConfig
from django.conf import settings
from django.db import connection


class PsSchemaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ps_schema'

    def ready(self):
        self.check_schema()

    def check_schema(self):
        database_schema = getattr(settings, 'DATABASE_SCHEMA', None)
        if not database_schema:
            return
        with connection.cursor() as cursor:
            cursor.execute(f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = '{database_schema}') THEN
                        CREATE SCHEMA {database_schema};
                    END IF;
                END
                $$;
            """)
