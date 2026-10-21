from sqlalchemy import text


def lock_inventory(db):
    """Serialize capacity checks and writes, including manual bookings and callbacks."""
    if db.get_bind().dialect.name != "sqlite":
        raise RuntimeError("Inventory locking must be implemented before changing the database backend")
    # Dependencies may already have opened a read transaction; no writes may precede this call.
    db.rollback()
    db.execute(text("BEGIN IMMEDIATE"))
