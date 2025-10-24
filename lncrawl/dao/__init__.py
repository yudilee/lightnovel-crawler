from typing import List, Type

from sqlalchemy import Table
from sqlmodel import SQLModel

from .artifact import Artifact
from .chapter import Chapter
from .job import Job
from .migration import Migration
from .novel import Novel
from .tag import Tag
from .user import User, VerifiedEmail
from .volume import Volume

models: List[Type[SQLModel]] = [
    Migration,
    User,
    VerifiedEmail,
    Tag,
    Novel,
    Chapter,
    Volume,
    Job,
    Artifact,
]

tables: List[Table] = [
    getattr(model, '__table__')
    for model in models
    if hasattr(model, '__table__')
]
