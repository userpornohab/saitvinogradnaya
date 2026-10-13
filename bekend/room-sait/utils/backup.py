"""SQLite online snapshots and verified, portable backup archives."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
import tarfile
from tempfile import TemporaryDirectory
import time
from uuid import uuid4


def snapshot_database(source: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / f"database-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid4().hex[:8]}.db"
    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as src:
        with closing(sqlite3.connect(target)) as dst:
            src.backup(dst)
            if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Backup integrity check failed")
    target.chmod(0o600)
    return target


def verify_archive(archive: Path):
    # Read every member (also verifies gzip CRC) and validate the SQLite snapshot.
    with TemporaryDirectory() as directory, tarfile.open(archive, "r:gz") as bundle:
        database = Path(directory) / "database.db"
        found = False
        for member in bundle:
            if member.issym() or member.islnk():
                raise RuntimeError("Backup contains a link")
            if not member.isfile():
                continue
            with bundle.extractfile(member) as stream:
                if member.name == "data/database.db":
                    with database.open("wb") as output:
                        while chunk := stream.read(1024 * 1024):
                            output.write(chunk)
                    found = True
                else:
                    while stream.read(1024 * 1024):
                        pass
        if not found:
            raise RuntimeError("Backup has no database")
        with closing(sqlite3.connect(database)) as db:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Invalid backup database")


def create_backup(database: Path, static: Path, destination: Path, keep=14):
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / f"vinegrape-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid4().hex[:8]}.tar.gz"
    pending = target.with_suffix(".tmp")
    try:
        with TemporaryDirectory() as directory:
            snapshot = snapshot_database(database, Path(directory))
            with tarfile.open(pending, "w:gz") as bundle:
                bundle.add(snapshot, arcname="data/database.db")
                for file in sorted(static.rglob("*")):
                    if file.is_file() and not file.is_symlink():
                        bundle.add(file, arcname="static/" + file.relative_to(static).as_posix())
        pending.chmod(0o600)
        verify_archive(pending)
        pending.replace(target)
    except Exception:
        pending.unlink(missing_ok=True)
        raise
    for old in sorted(destination.glob("vinegrape-*.tar.gz"), reverse=True)[max(keep, 1):]:
        old.unlink()
    return target


def restore_backup(archive: Path, destination: Path):
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Restore destination must be empty; live data is never overwritten")
    verify_archive(archive)
    root = destination.resolve()
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        for member in members:
            target = (root / member.name).resolve()
            if (not target.is_relative_to(root) or member.name.startswith("/")
                    or "\\" in member.name or member.issym() or member.islnk()
                    or not (member.name == "data/database.db" or member.name.startswith("static/"))):
                raise ValueError("Unsafe backup member")
        root.mkdir(parents=True, exist_ok=True)
        for member in members:
            if not member.isfile():
                continue
            target = root / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.extractfile(member) as src, target.open("xb") as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
            target.chmod(0o600)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--restore", type=Path)
    parser.add_argument("--restore-to", type=Path)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--database", type=Path, default=Path("data/database.db"))
    parser.add_argument("--static", type=Path, default=Path("static"))
    parser.add_argument("--destination", type=Path, default=Path("/backups"))
    args = parser.parse_args()
    if args.restore:
        if not args.restore_to:
            parser.error("--restore requires --restore-to (an empty directory)")
        restore_backup(args.restore, args.restore_to)
        print("Backup restored to " + str(args.restore_to), flush=True)
        return
    if args.verify:
        verify_archive(args.verify)
        print("Backup verified", flush=True)
        return
    while True:
        print(create_backup(args.database, args.static, args.destination,
                            int(os.getenv("BACKUP_KEEP", "14"))), flush=True)
        if not args.loop:
            break
        time.sleep(max(60, int(os.getenv("BACKUP_INTERVAL_SECONDS", "86400"))))


if __name__ == "__main__":
    main()
