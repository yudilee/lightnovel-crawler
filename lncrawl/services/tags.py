from typing import Any, List, Optional

from sqlmodel import and_, asc, func, select

from ..context import ctx
from ..dao import Tag
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated


class TagService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str = '',
    ) -> Paginated[Tag]:
        with ctx.db.session() as sess:
            stmt = select(Tag)
            cnt = select(func.count()).select_from(Tag)

            # Apply filters
            conditions: List[Any] = []

            if search:
                q = f"%{search.lower()}%"
                conditions.append(func.lower(Tag.name).like(q))

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(asc(Tag.name))

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

    def get(self, name: str) -> Tag:
        with ctx.db.session() as sess:
            tag = sess.get(Tag, name)
            if not tag:
                raise ServerErrors.no_such_tag
            return tag

    def update(self, name: str, description: Optional[str] = None) -> Tag:
        with ctx.db.session() as sess:
            tag = sess.get(Tag, name)
            if not tag:
                raise ServerErrors.no_such_tag
            if description is not None:
                tag.description = description
                sess.commit()
            return tag

    def delete(self, name: str) -> bool:
        with ctx.db.session() as sess:
            tag = sess.get(Tag, name)
            if not tag:
                return True
            sess.delete(tag)
            sess.commit()
            return True

    def batch_insert(self, names: List[str]) -> None:
        with ctx.db.session() as sess:
            existing = set(sess.exec(
                select(Tag.name).where(Tag.name.in_(names))  # type: ignore
            ).all())
            missing = [name for name in names if name not in existing]
            sess.add_all(Tag(name=name) for name in missing)
            sess.commit()
