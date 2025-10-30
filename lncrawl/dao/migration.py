from sqlmodel import Field, SQLModel


class Migration(SQLModel, table=True):
    id: int = Field(
        primary_key=True
    )
    version: int = Field(
        description="Current migration version"
    )
