from typing import List, Type

from sqlalchemy import Table
from sqlmodel import SQLModel

from .artifact import Artifact
from .chapter import Chapter
from .chapter_image import ChapterImage
from .enums import *  # noqa: F401,F403
from .job import Job
from .novel import Novel
from .read_history import ReadHistory
from .secrets import Secret
from .tag import Tag
from .user import User, VerifiedEmail
from .volume import Volume

models: List[Type[SQLModel]] = [
    User,
    VerifiedEmail,
    Tag,
    Novel,
    Volume,
    Chapter,
    ChapterImage,
    ReadHistory,
    Artifact,
    Job,
    Secret,
]

tables: List[Table] = [
    getattr(model, '__table__')
    for model in models
    if hasattr(model, '__table__')
]
