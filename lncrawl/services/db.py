import logging
from functools import cached_property
from pathlib import Path
from typing import Mapping, Optional, Sequence

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlmodel import Session, create_engine, inspect

from ..context import ctx

logger = logging.getLogger(__name__)


class DB:
    def __init__(self) -> None:
        pass

    @cached_property
    def engine(self):
        engine = create_engine(
            ctx.config.db.url,
            echo=ctx.logger.is_debug,
        )
        if ctx.logger.is_debug:
            engine.logger = logger
        logger.info(f'Database URL: "{engine.url}"')
        return engine

    def close(self):
        if "engine" in self.__dict__:
            self.engine.dispose()

    def session(
        self,
        *,
        autoflush: bool = True,
        expire_on_commit: bool = False,
        enable_baked_queries: bool = True,
    ):
        return Session(
            self.engine,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            enable_baked_queries=enable_baked_queries,
        )

    def exec(
        self,
        raw_sql: str,
        parameters: Optional[Sequence] = None,
        execution_options: Optional[Mapping] = None,
    ):
        r"""Executes a string SQL statement on the DBAPI cursor directly,
        without any SQL compilation steps.

         Multiple dictionaries::

             conn.exec_driver_sql(
                 "INSERT INTO table (id, value) VALUES (%(id)s, %(value)s)",
                 [{"id": 1, "value": "v1"}, {"id": 2, "value": "v2"}],
             )

         Single dictionary::

             conn.exec_driver_sql(
                 "INSERT INTO table (id, value) VALUES (%(id)s, %(value)s)",
                 dict(id=1, value="v1"),
             )

         Single tuple::

             conn.exec_driver_sql(
                 "INSERT INTO table (id, value) VALUES (?, ?)", (1, "v1")
             )

        """
        with self.engine.connect() as conn:
            return conn.exec_driver_sql(raw_sql, parameters, execution_options)

    # ------------------------------------------------------------------ #
    #                          Prepare Database                          #
    # ------------------------------------------------------------------ #

    @cached_property
    def alembic_config(self) -> Config:
        cfg = Config()
        migration_path = Path(__file__).parent.parent / "migrations"
        cfg.set_main_option("sqlalchemy.url", ctx.config.db.url)
        cfg.set_main_option("script_location", migration_path.as_posix())
        cfg.set_main_option(
            "file_template",
            r"%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d_%%(minute).2d_%%(second).2d_%%(slug)s",
        )
        cfg.set_section_option("post_write_hooks", "hooks", "black")
        cfg.set_section_option("post_write_hooks", "black.type", "console_scripts")
        cfg.set_section_option("post_write_hooks", "black.entrypoint", "black")
        cfg.set_section_option("post_write_hooks", "black.options", "REVISION_SCRIPT_FILENAME")
        return cfg

    def bootstrap(self):
        if self.has_any_tables() and self.current_revision() is None:
            command.stamp(self.alembic_config, self.base_revision())
        command.upgrade(self.alembic_config, "head")

    def has_any_tables(self):
        with self.engine.connect() as conn:
            return bool(inspect(conn).get_table_names())

    def current_revision(self):
        with self.engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()

    def base_revision(self):
        script = ScriptDirectory.from_config(ctx.db.alembic_config)
        base = script.get_base()
        assert base
        return base

    def latest_revision(self):
        script = ScriptDirectory.from_config(ctx.db.alembic_config)
        head = script.get_current_head()
        assert head
        return head
