"""Indexes for availability lookups."""
from alembic import op
from sqlalchemy import inspect

revision = "20261003_02"
down_revision = "20261003_01"


def upgrade():
    for table, columns in (
        ("bookings", ["room_id", "check_in_date", "check_out_date"]),
        ("calendar_sync_events", ["room_id", "start_date", "end_date"]),
        ("price_periods", ["room_id", "start_date", "end_date"]),
    ):
        name = f"ix_{table}_room_period"
        if name not in {index["name"] for index in inspect(op.get_bind()).get_indexes(table)}:
            op.create_index(name, table, columns)


def downgrade():
    for table in ("bookings", "calendar_sync_events", "price_periods"):
        op.drop_index(f"ix_{table}_room_period", table_name=table)
