"""Guest accounts, reservations and payment records. Existing bookings are untouched."""
from alembic import op
import sqlalchemy as sa

revision = "20261019_03"
down_revision = "20261003_02"


def upgrade():
    op.create_table("guest_profiles", sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("phone", sa.String(25), nullable=False), sa.Column("email_verified", sa.Boolean, nullable=False))
    op.create_table("guest_sessions", sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False), sa.Column("expires_at", sa.DateTime, nullable=False))
    op.create_index("ix_guest_sessions_user_id", "guest_sessions", ["user_id"])
    op.create_index("ix_guest_sessions_expires_at", "guest_sessions", ["expires_at"])
    op.create_table("guest_tokens", sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("purpose", sa.String(16), nullable=False), sa.Column("expires_at", sa.DateTime, nullable=False))
    op.create_index("ix_guest_tokens_user_id", "guest_tokens", ["user_id"])
    op.create_table("guest_request_limits", sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("count", sa.Integer, nullable=False), sa.Column("expires_at", sa.DateTime, nullable=False))
    op.create_table("payment_settings", sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("enabled", sa.Boolean, nullable=False), sa.Column("deposit_mode", sa.String(16), nullable=False),
        sa.Column("deposit_percent", sa.Integer, nullable=False), sa.Column("hold_minutes", sa.Integer, nullable=False),
        sa.Column("terms_url", sa.String(500), nullable=False), sa.Column("privacy_url", sa.String(500), nullable=False),
        sa.Column("terms_version", sa.String(50), nullable=False))
    op.create_table("guest_reservations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("booking_id", sa.Integer, sa.ForeignKey("bookings.id"), unique=True),
        sa.Column("room_title", sa.String(100), nullable=False),
        sa.Column("check_in_date", sa.Date, nullable=False), sa.Column("check_out_date", sa.Date, nullable=False),
        sa.Column("guests", sa.Integer, nullable=False), sa.Column("guest_name", sa.String(100), nullable=False),
        sa.Column("guest_phone", sa.String(25), nullable=False), sa.Column("email", sa.String(255), nullable=False),
        sa.Column("total_kopeks", sa.Integer, nullable=False), sa.Column("deposit_kopeks", sa.Integer, nullable=False),
        sa.Column("deposit_rule", sa.String(40), nullable=False), sa.Column("paid_kopeks", sa.Integer, nullable=False),
        sa.Column("status", sa.String(24), nullable=False), sa.Column("is_test", sa.Boolean, nullable=False),
        sa.Column("request_key", sa.String(64), nullable=False), sa.Column("terms_version", sa.String(50), nullable=False),
        sa.Column("terms_url", sa.String(500), nullable=False), sa.Column("receipt_json", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False), sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("paid_at", sa.DateTime), sa.Column("refund_reference", sa.String(200)),
        sa.Column("refund_admin_id", sa.Integer), sa.Column("refunded_at", sa.DateTime),
        sa.UniqueConstraint("user_id", "request_key"), sqlite_autoincrement=True)
    op.create_index("ix_guest_reservations_user_id", "guest_reservations", ["user_id"])
    op.create_index("ix_guest_reservation_capacity", "guest_reservations", ["room_id", "status", "expires_at"])
    op.create_table("guest_messages", sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("reservation_id", sa.Integer, sa.ForeignKey("guest_reservations.id"), nullable=False),
        sa.Column("sender_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_admin", sa.Boolean, nullable=False), sa.Column("body", sa.Text, nullable=False),
        sa.Column("request_key", sa.String(64), nullable=False), sa.Column("created_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("reservation_id", "sender_id", "request_key"))
    op.create_index("ix_guest_messages_reservation_id", "guest_messages", ["reservation_id"])


def downgrade():
    raise RuntimeError("Payment history must not be deleted. Restore a verified backup instead.")
