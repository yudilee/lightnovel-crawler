from typing import Any, List

from sqlmodel import and_, desc, func, select

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
            conditions.append(Novel.title != '...')
            conditions.append(Novel.title != '')

            if search:
                q = f"%{search.lower()}%"
                conditions.append(func.lower(Novel.title).like(q))

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
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                return True
            sess.delete(novel)
            sess.commit()
            return True
