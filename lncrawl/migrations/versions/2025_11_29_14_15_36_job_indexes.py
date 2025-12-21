"""Job Indexes

Revision ID: 2aa88e70f465
Revises: e80a0e357ec5
Create Date: 2025-11-29 14:15:36.837777
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2aa88e70f465"
down_revision: Union[str, Sequence[str], None] = "e80a0e357ec5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    dialect = op.get_context().dialect.name
except Exception:
    dialect = ''


def upgrade() -> None:
    """Upgrade schema."""
    if dialect != "sqlite":
        # Drop foreign key constraints temporarily
        op.drop_constraint(op.f("jobs_parent_job_id_fkey"), "jobs", type_="foreignkey")
        op.drop_constraint(op.f("jobs_depends_on_fkey"), "jobs", type_="foreignkey")

    # Drop old indexes
    op.drop_index(op.f("ix_job_is_done"), "jobs")
    op.drop_index(op.f("ix_job_parent_job_id"), "jobs")

    # Create new indexes
    op.create_index(op.f("ix_jobs_depends_on"), "jobs", ["depends_on", "is_done"], unique=False)
    op.create_index(op.f("ix_jobs_is_done"), "jobs", ["is_done"], unique=False)
    op.create_index(op.f("ix_jobs_ordering"), "jobs", ["priority", "user_id", "updated_at"], unique=False)
    op.create_index(op.f("ix_jobs_parent_job_id"), "jobs", ["parent_job_id"], unique=False)
    op.create_index(op.f("ix_jobs_scheduler"), "jobs", ["status", "done", "type"], unique=False)

    if dialect != "sqlite":
        # Recreate the foreign key constraints
        op.create_foreign_key(op.f("jobs_parent_job_id_fkey"), "jobs", "jobs", ["parent_job_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key(op.f("jobs_depends_on_fkey"), "jobs", "jobs", ["depends_on"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    if dialect != "sqlite":
        # Drop foreign key constraints temporarily
        op.drop_constraint(op.f("jobs_parent_job_id_fkey"), "jobs", type_="foreignkey")
        op.drop_constraint(op.f("jobs_depends_on_fkey"), "jobs", type_="foreignkey")

    # Drop indexes
    op.drop_index(op.f("ix_jobs_scheduler"), "jobs")
    op.drop_index(op.f("ix_jobs_parent_job_id"), "jobs")
    op.drop_index(op.f("ix_jobs_ordering"), "jobs")
    op.drop_index(op.f("ix_jobs_is_done"), "jobs")
    op.drop_index(op.f("ix_jobs_depends_on"), "jobs")

    # Create old indexes
    op.create_index(op.f("ix_job_parent_job_id"), "jobs", ["parent_job_id"], unique=False)
    op.create_index(op.f("ix_job_is_done"), "jobs", ["id", "is_done"], unique=False)

    if dialect != "sqlite":
        # Recreate the foreign key constraints
        op.create_foreign_key(op.f("jobs_parent_job_id_fkey"), "jobs", "jobs", ["parent_job_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key(op.f("jobs_depends_on_fkey"), "jobs", "jobs", ["depends_on"], ["id"], ondelete="CASCADE")
