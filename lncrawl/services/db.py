import logging
from typing import Mapping, Optional, Sequence

from sqlalchemy import inspect
from sqlmodel import Session, create_engine

from ..context import ctx
from ..dao import Migration, tables

logger = logging.getLogger(__name__)


class DB:
    def __init__(self) -> None:
        self.engine = create_engine(
            ctx.config.db.url,
            echo=ctx.logger.is_debug,
        )
        if ctx.logger.is_debug:
            self.engine.logger = logger
        logger.info(f'Database URL: "{self.engine.url}"')

    def close(self):
        logger.info('Disposing database engine')
        self.engine.dispose()

    def session(
        self, *,
        future: bool = True,
        autoflush: bool = True,
        autocommit: bool = False,
        expire_on_commit: bool = True,
        enable_baked_queries: bool = True,
    ):
        return Session(
            self.engine,
            future=future,  # type:ignore
            autoflush=autoflush,
            autocommit=autocommit,  # type:ignore
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

    def bootstrap(self):
        # create tables
        table = str(Migration.__tablename__)
        if not inspect(self.engine).has_table(table):
            logger.info(f'Creating {len(tables)} tables')
            self.__create_tables()
            return

        # check for migrations
        latest = DB.latest_version
        with self.session() as sess:
            entry = sess.get(Migration, 0)
            current = entry.version if entry else -1

        while current < latest:
            logger.info(f'Running migrations [{current}/{latest}]')
            current = self.__run_migration(current)
            sess.add(Migration(version=current))
            sess.commit()

    # ------------------------------------------------------------------ #
    #                           Table Creation                           #
    # ------------------------------------------------------------------ #

    def __create_tables(self, retry=2):
        try:
            for table in tables:
                table.create(self.engine, True)

            logger.info('Preparing migration table')
            with self.session() as sess:
                sess.add(Migration(version=self.latest_version))
                sess.commit()
        except Exception as e:
            if retry <= 0:
                raise
            logger.info(f'Retrying table creation. Cause: {repr(e)}')
            self.__create_tables(retry - 1)

    # ------------------------------------------------------------------ #
    #                         Database Migrations                        #
    # ------------------------------------------------------------------ #

    latest_version = 0
    """Latest migration version"""

    def __run_migration(self, version: int):
        raise ValueError(f'Unknown version {version}')
