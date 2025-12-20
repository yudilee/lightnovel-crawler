"""Novel Library

Revision ID: e6c4ce29ecfd
Revises: f3af583e88b4
Create Date: 2025-12-15 19:23:54.960861
"""

from typing import Sequence, Union

from sqlmodel.sql.sqltypes import AutoString
import sqlmodel as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e6c4ce29ecfd"
down_revision: Union[str, Sequence[str], None] = "f3af583e88b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "libraries",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("description", AutoString(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_libraries_created_at"), "libraries", ["created_at"], unique=False)
    op.create_index(op.f("ix_libraries_updated_at"), "libraries", ["updated_at"], unique=False)
    op.create_index(op.f("ix_libraries_user_id"), "libraries", ["user_id"], unique=False)
    op.create_index(op.f("ix_libraries_name"), "libraries", ["name"], unique=False)
    op.create_table(
        "library_novels",
        sa.Column("library_id", AutoString(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["library_id"],
            ["libraries.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["novel_id"],
            ["novels.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("library_id", "novel_id"),
        sa.UniqueConstraint("library_id", "novel_id", name="uix_library_novel"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("library_novels")
    op.drop_index(op.f("ix_libraries_name"), table_name="libraries")
    op.drop_index(op.f("ix_libraries_user_id"), table_name="libraries")
    op.drop_index(op.f("ix_libraries_updated_at"), table_name="libraries")
    op.drop_index(op.f("ix_libraries_created_at"), table_name="libraries")
    op.drop_table("libraries")
