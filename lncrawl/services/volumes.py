from typing import List

from sqlalchemy import delete as sa_delete
from sqlalchemy import insert as sa_insert
from sqlalchemy import update as sa_update
from sqlmodel import case, col, func, select

from ..context import ctx
from ..dao import User, Volume
from ..dao.enums import UserRole
from ..exceptions import ServerErrors
from ..models.volume import Volume as ModelVolume


class VolumeService:
    def __init__(self) -> None:
        pass

    def count(self, novel_id: str) -> int:
        with ctx.db.session() as sess:
            stmt = select(func.count()).select_from(Volume)
            stmt = stmt.where(Volume.novel_id == novel_id)
            return sess.exec(stmt).one()

    def list(self, novel_id: str) -> List[Volume]:
        with ctx.db.session() as sess:
            stmt = select(Volume)
            stmt = stmt.where(Volume.novel_id == novel_id)
            stmt = stmt.order_by(col(Volume.serial).asc())
            items = sess.exec(stmt).all()
            return list(items)

    def get(self, volume_id: str) -> Volume:
        with ctx.db.session() as sess:
            volume = sess.get(Volume, volume_id)
            if not volume:
                raise ServerErrors.no_such_volume
            return volume

    def get_many(self, volume_ids: List[str]) -> List[Volume]:
        with ctx.db.session() as sess:
            stmt = select(Volume).where(col(Volume.id).in_(volume_ids))
            items = sess.exec(stmt).all()
            return list(items)

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

    def sync(self, novel_id: str, volumes: List[ModelVolume]):
        with ctx.db.session() as sess:
            wanted = {
                v.id: v for v in volumes
            }
            existing = {
                v.serial: v
                for v in sess.exec(
                    select(Volume).where(Volume.novel_id == novel_id)
                ).all()
            }

            wk = set(wanted.keys())
            ek = set(existing.keys())
            to_insert = wk - ek
            to_delete = ek - wk
            to_update = ek & wk

            if to_insert:
                sess.exec(
                    sa_insert(Volume),
                    params=[
                        Volume(
                            novel_id=novel_id,
                            serial=s,
                            title=wanted[s].title,
                            extra=dict(wanted[s].extra),
                        ).model_dump()
                        for s in to_insert
                    ]
                )

            if to_update:
                title_updates = {}
                for s in to_update:
                    row = existing[s]
                    rid = row.id
                    title = wanted[s].title
                    if row.title != title:
                        title_updates[rid] = title
                if title_updates:
                    sess.exec(
                        sa_update(Volume)
                        .where(col(Volume.id).in_(title_updates.keys()))
                        .values(
                            title=case(title_updates, value=Volume.id),
                        )
                    )

            if to_delete:
                sess.exec(
                    sa_delete(Volume)
                    .where(col(Volume.novel_id) == novel_id)
                    .where(col(Volume.serial).in_(to_delete))
                )

            sess.commit()
