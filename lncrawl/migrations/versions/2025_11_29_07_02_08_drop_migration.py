"""Drop Migration

Revision ID: e80a0e357ec5
Revises: 4d43af0bd879
Create Date: 2025-11-29 07:02:08.563414
"""

from typing import Sequence, Union

import sqlmodel as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e80a0e357ec5"
down_revision: Union[str, Sequence[str], None] = "4d43af0bd879"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ''


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("_migration")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "_migration",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("version", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("_migration_pkey")),
    )
