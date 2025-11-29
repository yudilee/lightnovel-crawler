"""Base

Revision ID: 4d43af0bd879
Revises:
Create Date: 2025-11-29 05:19:27.241736
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlmodel.sql.sqltypes import AutoString

from lncrawl.dao import enums

# revision identifiers, used by Alembic.
revision: str = "4d43af0bd879"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "_migration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "novels",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("domain", AutoString(), nullable=False),
        sa.Column("url", AutoString(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("authors", AutoString(), nullable=True),
        sa.Column("synopsis", AutoString(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("cover_url", AutoString(), nullable=True),
        sa.Column("mtl", sa.Boolean(), nullable=False),
        sa.Column("rtl", sa.Boolean(), nullable=False),
        sa.Column("manga", sa.Boolean(), nullable=False),
        sa.Column("language", sa.CHAR(length=2), nullable=True),
        sa.Column("volume_count", sa.Integer(), nullable=False),
        sa.Column("chapter_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index(
        op.f("ix_novels_created_at"),
        "novels",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_novels_domain"),
        "novels",
        ["domain"],
        unique=False,
    )
    op.create_index(
        op.f("ix_novels_updated_at"),
        "novels",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "tags",
        sa.Column("name", AutoString(), nullable=False),
        sa.Column("description", AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("referrer_id", AutoString(), nullable=True),
        sa.Column("password", AutoString(), nullable=False),
        sa.Column("email", AutoString(), nullable=False),
        sa.Column("name", AutoString(), nullable=True),
        sa.Column("role", sa.Enum(enums.UserRole, name="userrole"), nullable=False),
        sa.Column("tier", sa.Enum(enums.UserTier, name="usertier"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["referrer_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_users_created_at"),
        "users",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )
    op.create_index(
        op.f("ix_users_updated_at"),
        "users",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "verifiedemail",
        sa.Column("email", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("email"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("parent_job_id", AutoString(), nullable=True),
        sa.Column("depends_on", AutoString(), nullable=True),
        sa.Column("type", sa.Enum(enums.JobType, name="jobtype"), nullable=False),
        sa.Column("priority", sa.Enum(enums.JobPriority, name="jobpriority"), nullable=False),
        sa.Column("status", sa.Enum(enums.JobStatus, name="jobstatus"), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("error", AutoString(), nullable=True),
        sa.Column("started_at", sa.BigInteger(), nullable=True),
        sa.Column("finished_at", sa.BigInteger(), nullable=True),
        sa.Column("done", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["depends_on"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_job_is_done",
        "jobs",
        ["id", "is_done"],
        unique=False,
    )
    op.create_index(
        "ix_job_parent_job_id",
        "jobs",
        ["parent_job_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_jobs_created_at"),
        "jobs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_jobs_updated_at"),
        "jobs",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "secrets",
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("name", AutoString(length=255), nullable=False),
        sa.Column("value", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_index(
        op.f("ix_secrets_created_at"),
        "secrets",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_secrets_name"),
        "secrets",
        ["name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_secrets_user_id"),
        "secrets",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "volumes",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("serial", sa.Integer(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("chapter_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("novel_id", "serial"),
    )
    op.create_index(
        "ix_volume_novel_id",
        "volumes",
        ["novel_id"],
        unique=False,
    )
    op.create_index(
        "ix_volume_novel_serial",
        "volumes",
        ["novel_id", "serial"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volumes_created_at"),
        "volumes",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volumes_updated_at"),
        "volumes",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "artifacts",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("job_id", AutoString(), nullable=True),
        sa.Column("user_id", AutoString(), nullable=True),
        sa.Column("format", sa.Enum(enums.OutputFormat, name="outputformat"), nullable=False),
        sa.Column("file_name", AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_artifacts_created_at"),
        "artifacts",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_artifacts_format"),
        "artifacts",
        ["format"],
        unique=False,
    )
    op.create_index(
        op.f("ix_artifacts_novel_id"),
        "artifacts",
        ["novel_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_artifacts_updated_at"),
        "artifacts",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "chapters",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("serial", sa.Integer(), nullable=False),
        sa.Column("volume_id", AutoString(), nullable=True),
        sa.Column("url", AutoString(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["volume_id"], ["volumes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("novel_id", "serial"),
    )
    op.create_index(
        "ix_chapter_novel_id",
        "chapters",
        ["novel_id"],
        unique=False,
    )
    op.create_index(
        "ix_chapter_novel_serial",
        "chapters",
        ["novel_id", "serial"],
        unique=False,
    )
    op.create_index(
        "ix_chapter_novel_volume",
        "chapters",
        ["novel_id", "volume_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chapters_created_at"),
        "chapters",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chapters_updated_at"),
        "chapters",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "chapter_images",
        sa.Column("id", AutoString(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("extra", sa.JSON(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("chapter_id", AutoString(), nullable=False),
        sa.Column("url", AutoString(), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_chapter_image_chapter",
        "chapter_images",
        ["chapter_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chapter_images_created_at"),
        "chapter_images",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chapter_images_updated_at"),
        "chapter_images",
        ["updated_at"],
        unique=False,
    )
    op.create_table(
        "read_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("user_id", AutoString(), nullable=False),
        sa.Column("chapter_id", AutoString(), nullable=False),
        sa.Column("novel_id", AutoString(), nullable=False),
        sa.Column("volume_id", AutoString(), nullable=True),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["novel_id"], ["novels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["volume_id"], ["volumes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "chapter_id"),
    )
    op.create_index(
        "ix_read_history_user_created",
        "read_history",
        ["user_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
