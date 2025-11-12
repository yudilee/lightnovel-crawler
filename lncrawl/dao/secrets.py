from sqlmodel import BigInteger, Field, LargeBinary, SQLModel

from ..utils.time_utils import current_timestamp


class Secret(SQLModel, table=True):
    __tablename__ = 'secrets'  # type: ignore

    user_id: str = Field(
        index=True,
        foreign_key="users.id",
        ondelete='CASCADE'
    )
    name: str = Field(
        primary_key=True,
        index=True,
        nullable=False,
        max_length=255,
        description="Secret name"
    )
    value: bytes = Field(
        exclude=True,
        sa_type=LargeBinary,
        description="Encrypted secret value"
    )
    created_at: int = Field(
        index=True,
        default_factory=current_timestamp,
        sa_type=BigInteger
    )
