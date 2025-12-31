"""Feedback

Revision ID: 2c1b5463eecb
Revises: 4a8ea5ca1d18
Create Date: 2025-12-23 22:52:47.353162
"""

from typing import Sequence, Union

import sqlmodel as sa
from alembic import op
from sqlmodel.sql.sqltypes import AutoString

from lncrawl.dao import enums

# revision identifiers, used by Alembic.
revision: str = "2c1b5463eecb"
down_revision: Union[str, Sequence[str], None] = "4a8ea5ca1d18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "feedback",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("type", sa.Enum(enums.FeedbackType, name="feedbacktype"), nullable=False),
        sa.Column("status", sa.Enum(enums.FeedbackStatus, name="feedbackstatus"), nullable=False),
        sa.Column("subject", AutoString(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("feedback_user_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("feedback_pkey")),
    )
    op.create_index(op.f("ix_feedback_created_at"), "feedback", ["created_at"], unique=False)
    op.create_index(op.f("ix_feedback_status"), "feedback", ["status"], unique=False)
    op.create_index(op.f("ix_feedback_type"), "feedback", ["type"], unique=False)
    op.create_index(op.f("ix_feedback_user_id"), "feedback", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    if dialect != "sqlite":
        op.drop_constraint(op.f("feedback_user_id_fkey"), "feedback", type_="foreignkey")

    op.drop_index(op.f("ix_feedback_user_id"), "feedback")
    op.drop_index(op.f("ix_feedback_type"), "feedback")
    op.drop_index(op.f("ix_feedback_status"), "feedback")
    op.drop_index(op.f("ix_feedback_created_at"), "feedback")

    op.drop_table("feedback")

    if dialect == "postgresql":
        op.execute("DROP TYPE IF EXISTS feedbacktype")
        op.execute("DROP TYPE IF EXISTS feedbackstatus")
