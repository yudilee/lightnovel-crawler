from typing import Any, List

from sqlmodel import and_, asc, func, select

from ..context import ctx
from ..dao import User, Volume
from ..dao.enums import UserRole
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated


class VolumeService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        search: str = '',
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[Volume]:
        with ctx.db.session() as sess:
            stmt = select(Volume)
            cnt = select(func.count()).select_from(Volume)

            # Apply filters
            conditions: List[Any] = []

            if search:
                q = f"%{search.lower()}%"
                conditions.append(func.lower(Volume.title).like(q))

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(asc(Volume.serial))

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

    def get(self, volume_id: str) -> Volume:
        with ctx.db.session() as sess:
            volume = sess.get(Volume, volume_id)
            if not volume:
                raise ServerErrors.no_such_volume
            return volume

    def delete(self, volume_id: str, user: User) -> bool:
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
        with ctx.db.session() as sess:
            volume = sess.get(Volume, volume_id)
            if not volume:
                return True
            sess.delete(volume)
            sess.commit()
            return True

    def find(self, novel_id: str, serial: int) -> Volume:
        with ctx.db.session() as sess:
            stmt = select(Volume).where(
                Volume.novel_id == novel_id,
                Volume.serial == serial,
            )
            volume = sess.exec(stmt).first()
            if not volume:
                raise ServerErrors.no_such_volume
            return volume
