"""Adopt the existing application schema without replaying destructive legacy migrations."""
from alembic import op
from sqlalchemy import inspect, text
import json
from pathlib import Path

revision = "20261003_01"
down_revision = None

# Only these additions were previously applied by main.py at import time.
ADDITIONS = {
    "rooms": {"calendar_token": "VARCHAR(64)"},
    "room_photos": {"sort_order": "INTEGER DEFAULT 0"},
    "courtyard_photos": {"category": "VARCHAR(30) DEFAULT 'yard'", "sort_order": "INTEGER DEFAULT 0"},
}


def upgrade():
    connection = op.get_bind()
    if connection.dialect.name != "sqlite":
        raise RuntimeError("This deployment baseline targets SQLite. Plan a separate migration for other databases.")
    baseline = json.loads((Path(__file__).resolve().parents[1] / "baseline.json").read_text(encoding="utf-8"))
    inspector = inspect(connection)
    # Reject unsupported older schemas before changing anything; never drop guest data.
    for name, table in baseline.items():
        if inspector.has_table(name):
            existing = {column["name"] for column in inspector.get_columns(name)}
            missing = set(table["columns"]) - existing - set(ADDITIONS.get(name, {}))
            if missing:
                raise RuntimeError(f"Unsupported schema: {name} missing {sorted(missing)}. Restore/check the database before upgrading.")
    for name, table in baseline.items():
        if not inspector.has_table(name):
            connection.execute(text(table["create"]))
            for index in table["indexes"]:
                connection.execute(text(index))
    for table_name, columns in ADDITIONS.items():
        existing = {column["name"] for column in inspect(connection).get_columns(table_name)}
        for name, definition in columns.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {name} {definition}"))
    connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_rooms_calendar_token ON rooms(calendar_token)"))


def downgrade():
    raise RuntimeError("Restore a verified backup to undo adoption; automatic data deletion is disabled.")
