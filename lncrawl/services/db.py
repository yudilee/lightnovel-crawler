import logging
from typing import Mapping, Optional, Sequence

from sqlalchemy import inspect
from sqlmodel import Session, create_engine

from ..context import ctx
from ..dao import Migration, tables

logger = logging.getLogger(__name__)


class DB:
    # ------------------------------------------------------------------ #
    migration_id = 1       # Migration row id
    latest_version = 1     # Latest migration version
    # ------------------------------------------------------------------ #

    def __init__(self) -> None:
        self.engine = create_engine(
            ctx.config.db.url,
            echo=ctx.logger.is_debug,
        )
        if ctx.logger.is_debug:
            self.engine.logger = logger
        logger.info(f'Database URL: "{self.engine.url}"')

    @property
    def is_postgres(self):
        return self.engine.dialect.name == "postgresql"

    def close(self):
        self.engine.dispose()

    def session(
        self, *,
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

    def bootstrap(self):
        # ensure tables
        table = str(Migration.__tablename__)
        inspector = inspect(self.engine)
        if not inspector.has_table(table):
            logger.info(f'Creating {len(tables)} tables')
            self.__create_tables()
        else:
            self.__run_migrations()

        # ensure admin user
        ctx.users.insert_admin()

    # ------------------------------------------------------------------ #
    #                           Table Creation                           #
    # ------------------------------------------------------------------ #

    def __create_tables(self, retry=2):
        try:
            for table in tables:
                table.create(self.engine, True)

            logger.info('Preparing migration table')
            with self.session() as sess:
                entry = Migration(
                    id=DB.migration_id,
                    version=DB.latest_version,
                )
                sess.add(entry)
                sess.commit()
        except Exception as e:
            if retry <= 0:
                raise
            logger.info(f'Retrying table creation. Cause: {repr(e)}')
            self.__create_tables(retry - 1)

    # ------------------------------------------------------------------ #
    #                         Database Migrations                        #
    # ------------------------------------------------------------------ #

    def __run_migrations(self):
        latest = DB.latest_version
        with self.session() as sess:
            entry = sess.get_one(Migration, DB.migration_id)
            current = entry.version
            while current < latest:
                logger.info(f'Running migrations: {current} -> {latest}')
                self.__migrate_next(current)
                current += 1
                entry.version = current
                sess.commit()

    def __migrate_next(self, version: int) -> None:
        raise ValueError(f'Unknown version {version}')
