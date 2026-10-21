"""Non-destructive adoption of the deployed schema; independent of legacy revisions."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from database.database import engine
from utils.backup import snapshot_database

HEAD = "20261019_03"


def upgrade_database(target_engine=engine):
    root = Path(__file__).resolve().parents[1]
    config = Config()
    config.set_main_option("script_location", str(root / "deployment_migrations"))
    with target_engine.connect() as connection:
        inspector = inspect(connection)
        revision = None
        if inspector.has_table("deployment_schema_version"):
            revision = connection.execute(text("SELECT version_num FROM deployment_schema_version")).scalar()
        connection.rollback()
        if revision == HEAD:
            return
        if target_engine.dialect.name == "sqlite":
            database = target_engine.url.database
            if database and database != ":memory:" and Path(database).exists():
                snapshot_database(Path(database), Path(database).parent / "migration-backups")
            # Serialize concurrent startups before schema inspection and changes.
            connection.exec_driver_sql("BEGIN IMMEDIATE")
        else:
            connection.begin()
        try:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
            connection.commit()
        except Exception:
            connection.rollback()
            raise


if __name__ == "__main__":
    upgrade_database()
