import shutil
from typing import Any, Generator, List, Optional

import sqlmodel as sa

from ..context import ctx
from ..dao import Novel
from ..exceptions import ServerErrors
from ..server.models import Paginated
from ..services.sources.dto import SourceItem


class NovelService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        search: str = '',
        offset: int = 0,
        limit: int = 20,
        domain: str = '',
    ) -> Paginated[Novel]:
        with ctx.db.session() as sess:
            stmt = sa.select(Novel)
            cnt = sa.select(sa.func.count()).select_from(Novel)

            # Apply filters
            conditions: List[Any] = []

            if domain:
                conditions.append(sa.col(Novel.url).ilike(f'%{domain}%'))

            if search:
                conditions.append(sa.col(Novel.title).ilike(f"%{search}%"))

            if conditions:
                cnd = sa.and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(sa.desc(Novel.updated_at))

            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)

            total = sess.exec(cnt).one()
            items = sess.exec(stmt).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def list_sources(self) -> Generator[SourceItem, None, None]:
        with ctx.db.session() as sess:
            domains = sess.scalars(sa.select(sa.func.distinct(Novel.domain)))
            for domain in domains:
                yield from ctx.sources.list(domain)

    def get(self, novel_id: str) -> Novel:
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise ServerErrors.no_such_novel
            return novel

    def delete(self, novel_id: str) -> bool:
        novel_dir = ctx.files.resolve(f'novels/{novel_id}')
        shutil.rmtree(novel_dir, True)
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                return True
            sess.delete(novel)
            sess.commit()
            return True

    def find_by_url(self, novel_url: str) -> Optional[Novel]:
        with ctx.db.session() as sess:
            return sess.exec(
                sa.select(Novel)
                .where(Novel.url == novel_url)
            ).first()
