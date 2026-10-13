"""Rehearse migrations on a temporary snapshot without changing the source database."""
import argparse
from contextlib import closing
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from sqlalchemy import create_engine

from database.migrate import upgrade_database
from utils.backup import snapshot_database


def read_rows(path):
    with closing(sqlite3.connect(path)) as db:
        tables = [name for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'deployment_schema_version'")]
        return {name: ([column[1] for column in db.execute(f'PRAGMA table_info("{name}")')],
                       db.execute(f'SELECT * FROM "{name}" ORDER BY rowid').fetchall()) for name in tables}


def check_upgrade(source):
    with TemporaryDirectory() as directory:
        snapshot = snapshot_database(source, Path(directory))
        before = read_rows(snapshot)
        engine = create_engine("sqlite:///" + snapshot.as_posix())
        try:
            upgrade_database(engine)
            upgrade_database(engine)
            with closing(sqlite3.connect(snapshot)) as db:
                for table, (columns, rows) in before.items():
                    names = ",".join('"' + name.replace('"', '""') + '"' for name in columns)
                    after = db.execute(f'SELECT {names} FROM "{table}" ORDER BY rowid').fetchall()
                    if after != rows:
                        raise RuntimeError(f"Existing data changed in {table}")
        finally:
            engine.dispose()
        print(f"Migration rehearsal passed: {len(before)} existing tables preserved. Source unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    check_upgrade(parser.parse_args().database)
