from typing import Any, Dict, List, Optional

from sqlalchemy import delete as sa_delete
from sqlalchemy import insert as sa_insert
from sqlmodel import and_, asc, func, select

from ..context import ctx
from ..dao import Chapter, Volume
from ..exceptions import ServerErrors
from ..models import Chapter as ModelChapter
from ..server.models.pagination import Paginated


class ChapterService:
    def __init__(self) -> None:
        pass

    def count(self, novel_id: str) -> int:
        with ctx.db.session() as sess:
            stmt = select(func.count()).select_from(Chapter)
            stmt = stmt.where(Chapter.novel_id == novel_id)
            return sess.exec(stmt).one()

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

    def delete(self, chapter_id: str) -> bool:
        with ctx.db.session() as sess:
            chapter = sess.get(Chapter, chapter_id)
            if not chapter:
                return True
            ctx.files.resolve(chapter.content_file).unlink(True)
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

    def sync(self, novel_id: str, chapters: List[ModelChapter]):
        with ctx.db.session() as sess:
            vol_id_map: Dict[Optional[int], str] = {
                v.serial: v.id
                for v in sess.exec(
                    select(Volume).where(Volume.novel_id == novel_id)
                ).all()
            }

            wanted = {
                c.id: c for c in chapters
            }
            existing = {
                c.serial: c
                for c in sess.exec(
                    select(Chapter).where(Chapter.novel_id == novel_id)
                ).all()
            }

            wk = set(wanted.keys())
            ek = set(existing.keys())
            to_insert = wk - ek
            to_delete = ek - wk
            to_update = wk & ek

            if to_insert:
                sess.exec(
                    sa_insert(Chapter),
                    params=[
                        Chapter(
                            novel_id=novel_id,
                            serial=s,
                            url=wanted[s].url,
                            title=wanted[s].title,
                            extra=wanted[s].extras,
                            volume_id=vol_id_map.get(wanted[s].volume),
                        ).model_dump()
                        for s in to_insert
                    ]
                )
            if to_update:
                for serial in to_update:
                    model = wanted[serial]
                    chapter = existing[serial]
                    chapter.url = model.url
                    chapter.title = model.title
                    chapter.volume_id = vol_id_map.get(model.volume)
                    chapter.extra = model.extras
            if to_delete:
                sess.exec(
                    sa_delete(Chapter)
                    .where(
                        and_(
                            Chapter.novel_id == novel_id,
                            Chapter.serial.in_(to_delete),  # type: ignore
                        )
                    )
                )
                for serial in to_delete:
                    file = existing[serial].content_file
                    ctx.files.resolve(file).unlink(True)

            sess.commit()
