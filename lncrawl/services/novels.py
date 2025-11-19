import shutil
from typing import Any, List, Optional

from sqlmodel import and_, desc, col, func, select

from ..context import ctx
from ..dao import Novel
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated


class NovelService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        search: str = '',
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[Novel]:
        with ctx.db.session() as sess:
            stmt = select(Novel)
            cnt = select(func.count()).select_from(Novel)

            # Apply filters
            conditions: List[Any] = []

            if search:
                q = f"%{search.lower()}%"
                conditions.append(col(Novel.title).ilike(q))

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(desc(Novel.updated_at))

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
                select(Novel)
                .where(Novel.url == novel_url)
            ).first()
