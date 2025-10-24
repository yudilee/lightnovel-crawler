from typing import Any, List, Optional

from sqlmodel import and_, asc, func, select

from ..context import ctx
from ..dao import Chapter, User
from ..dao.enums import UserRole
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated


class ChapterService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str = '',
        volume_id: Optional[str] = None,
        novel_id: Optional[str] = None,
    ) -> Paginated[Chapter]:
        with ctx.db.session() as sess:
            stmt = select(Chapter)
            cnt = select(func.count()).select_from(Chapter)

            # Apply filters
            conditions: List[Any] = []

            if search:
                q = f"%{search.lower()}%"
                conditions.append(func.lower(Chapter.title).like(q))

            if novel_id:
                conditions.append(Chapter.novel_id == novel_id)

            if volume_id:
                conditions.append(Chapter.volume_id == volume_id)

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(asc(Chapter.serial))

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

    def get(self, chapter_id: str) -> Chapter:
        with ctx.db.session() as sess:
            chapter = sess.get(Chapter, chapter_id)
            if not chapter:
                raise ServerErrors.no_such_chapter
            return chapter

    def delete(self, chapter_id: str, user: User) -> bool:
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
        with ctx.db.session() as sess:
            chapter = sess.get(Chapter, chapter_id)
            if not chapter:
                return True
            sess.delete(chapter)
            sess.commit()
            return True

    def find(self, novel_id: str, serial: int) -> Chapter:
        with ctx.db.session() as sess:
            stmt = select(Chapter).where(
                Chapter.novel_id == novel_id,
                Chapter.serial == serial,
            )
            volume = sess.exec(stmt).first()
            if not volume:
                raise ServerErrors.no_such_volume
            return volume
