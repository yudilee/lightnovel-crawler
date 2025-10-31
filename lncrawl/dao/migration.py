from sqlmodel import Field, SQLModel


class Migration(SQLModel, table=True):
    __tablename__ = '_migration'  # type: ignore
    id: int = Field(
        primary_key=True
    )
    version: int = Field(
        description="Current migration version"
    )
