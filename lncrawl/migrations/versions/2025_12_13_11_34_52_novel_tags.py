"""Novel tags

Revision ID: f3af583e88b4
Revises: 2aa88e70f465
Create Date: 2025-12-13 11:34:52.707361
"""

from typing import Sequence, Union

import sqlmodel as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f3af583e88b4"
down_revision: Union[str, Sequence[str], None] = "2aa88e70f465"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.alter_column("novels", "tags", existing_type=postgresql.JSON(astext_type=sa.Text()), nullable=False)
    elif dialect == "sqlite":
        with op.batch_alter_table("novels") as batch_op:
            batch_op.alter_column("tags", existing_type=sa.JSON(), nullable=False)
    else:
        op.alter_column("novels", "tags", existing_type=sa.JSON(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.alter_column("novels", "tags", existing_type=postgresql.JSON(astext_type=sa.Text()), nullable=True)
    elif dialect == "sqlite":
        with op.batch_alter_table("novels") as batch_op:
            batch_op.alter_column("tags", existing_type=sa.JSON(), nullable=True)
    else:
        op.alter_column("novels", "tags", existing_type=sa.JSON(), nullable=True)
