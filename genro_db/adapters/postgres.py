"""PostgreSQL database adapter."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from .base import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):
    """Adapter for PostgreSQL databases."""

    @property
    def type_map(self) -> dict[type, str]:
        """Map Python types to PostgreSQL types."""
        return {
            str: 'VARCHAR',
            int: 'BIGINT',
            float: 'DOUBLE PRECISION',
            bool: 'BOOLEAN',
            bytes: 'BYTEA',
            Decimal: 'NUMERIC',
            date: 'DATE',
            datetime: 'TIMESTAMP',
            time: 'TIME',
        }

    def get_current_schema(self, cursor: Any, table_name: str) -> dict:
        """
        Get current table schema from PostgreSQL.

        Uses information_schema.columns to retrieve column information.
        """
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
            """,
            (table_name,)
        )

        schema = {}
        for row in cursor.fetchall():
            schema[row['column_name']] = {
                'name': row['column_name'],
                'type': row['data_type'],
                'notnull': 1 if row['is_nullable'] == 'NO' else 0,
                'dflt_value': row['column_default'],
            }

        return schema

    def supports_drop_column(self) -> bool:
        """PostgreSQL supports DROP COLUMN."""
        return True

    def get_autoincrement_syntax(self) -> str:
        """
        Get AUTOINCREMENT syntax for PostgreSQL.

        PostgreSQL uses SERIAL or GENERATED ... AS IDENTITY.
        """
        return 'SERIAL'

    def _table_exists(self, cursor: Any, table_name: str) -> bool:
        """Check if table exists in PostgreSQL database."""
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
            """,
            (table_name,)
        )
        return cursor.fetchone()[0]

    def _drop_columns(self, cursor: Any, table: Any, columns: set[str]) -> list[str]:
        """
        Drop columns from PostgreSQL table.

        PostgreSQL supports DROP COLUMN directly.
        """
        migrations = []

        for col_name in columns:
            sql = f"ALTER TABLE {table.sql_name} DROP COLUMN {col_name}"
            cursor.execute(sql)
            migrations.append(sql)

        return migrations
