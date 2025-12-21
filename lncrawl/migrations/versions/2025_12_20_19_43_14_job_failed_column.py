"""Job failed column

Revision ID: 4a8ea5ca1d18
Revises: e6c4ce29ecfd
Create Date: 2025-12-20 19:43:14.805104
"""

from typing import Sequence, Union

import sqlmodel as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4a8ea5ca1d18"
down_revision: Union[str, Sequence[str], None] = "e6c4ce29ecfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ''


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("jobs", sa.Column("failed", sa.Integer(), server_default=sa.literal(0), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("jobs", "failed")
