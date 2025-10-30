from typing import Dict, List, Optional

from sqlalchemy import delete as sa_delete
from sqlalchemy import insert as sa_insert
from sqlalchemy import update as sa_update
from sqlmodel import case, col, func, select

from ..context import ctx
from ..dao import Chapter, Volume
from ..exceptions import ServerErrors
from ..models import Chapter as ModelChapter


class ChapterService:
    def __init__(self) -> None:
        pass

    def count(
        self, *,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
    ) -> int:
        with ctx.db.session() as sess:
            stmt = select(func.count()).select_from(Chapter)
            if novel_id:
                stmt = stmt.where(Chapter.novel_id == novel_id)
            if volume_id:
                stmt = stmt.where(Chapter.volume_id == volume_id)
            return sess.exec(stmt).one()

    def list(
        self, *,
        novel_id: Optional[str] = None,
        volume_id: Optional[str] = None,
    ) -> List[Chapter]:
        with ctx.db.session() as sess:
            stmt = select(Chapter)
            if novel_id:
                stmt = stmt.where(Chapter.novel_id == novel_id)
            if volume_id:
                stmt = stmt.where(Chapter.volume_id == volume_id)
            stmt = stmt.order_by(col(Chapter.serial).asc())
            items = sess.exec(stmt).all()
            return list(items)

    def find(self, novel_id: str, serial: int) -> Chapter:
        with ctx.db.session() as sess:
            stmt = select(Chapter).where(
                Chapter.novel_id == novel_id,
                Chapter.serial == serial,
            )
            chapter = sess.exec(stmt).first()
            if not chapter:
                raise ServerErrors.no_such_chapter
            return chapter

    def get(self, chapter_id: str) -> Chapter:
        with ctx.db.session() as sess:
            chapter = sess.get(Chapter, chapter_id)
            if not chapter:
                raise ServerErrors.no_such_chapter
            return chapter

    def get_many(self, chapter_ids: List[str]) -> List[Chapter]:
        with ctx.db.session() as sess:
            stmt = select(Chapter).where(col(Chapter.id).in_(chapter_ids))
            items = sess.exec(stmt).all()
            return list(items)

    def delete(self, chapter_id: str) -> None:
        with ctx.db.session() as sess:
            chapter = sess.get(Chapter, chapter_id)
            if not chapter:
                return
            ctx.files.resolve(chapter.content_file).unlink(True)
            sess.delete(chapter)
            sess.commit()

    def sync(self, novel_id: str, chapters: List[ModelChapter]):
        with ctx.db.session() as sess:
            vol_id_map: Dict[Optional[int], str] = {
                v.serial: v.id
                for v in sess.exec(
                    select(Volume)
                    .where(Volume.novel_id == novel_id)
                ).all()
            }

            wanted = {
                c.id: c for c in chapters
            }
            existing = {
                c.serial: c
                for c in sess.exec(
                    select(Chapter)
                    .where(Chapter.novel_id == novel_id)
                ).all()
            }

            wk = set(wanted.keys())
            ek = set(existing.keys())
            to_insert = wk - ek
            to_delete = ek - wk
            to_update = ek & wk

            if to_insert:
                sess.exec(
                    sa_insert(Chapter),
                    params=[
                        Chapter(
                            serial=s,
                            novel_id=novel_id,
                            url=wanted[s].url,
                            title=wanted[s].title,
                            extra=dict(wanted[s].extra),
                            volume_id=vol_id_map.get(wanted[s].volume),
                        ).model_dump()
                        for s in to_insert
                    ]
                )

            if to_update:
                url_updates = {}
                title_updates = {}
                volume_updates = {}
                for s in to_update:
                    row = existing[s]
                    rid = row.id
                    url = wanted[s].url
                    title = wanted[s].title
                    vol_id = vol_id_map.get(wanted[s].volume)
                    if row.url != url:
                        url_updates[rid] = url
                    if row.title != title:
                        title_updates[rid] = title
                    if row.volume_id != vol_id:
                        volume_updates[rid] = vol_id
                if url_updates:
                    sess.exec(
                        sa_update(Chapter)
                        .where(col(Chapter.id).in_(url_updates.keys()))
                        .values(
                            url=case(url_updates, value=Chapter.id),
                        )
                    )
                if title_updates:
                    sess.exec(
                        sa_update(Chapter)
                        .where(col(Chapter.id).in_(title_updates.keys()))
                        .values(
                            title=case(title_updates, value=Chapter.id),
                        )
                    )
                if volume_updates:
                    sess.exec(
                        sa_update(Chapter)
                        .where(col(Chapter.id).in_(volume_updates.keys()))
                        .values(
                            volume_id=case(volume_updates, value=Chapter.id),
                        )
                    )

            if to_delete:
                sess.exec(
                    sa_delete(Chapter)
                    .where(col(Chapter.novel_id) == novel_id)
                    .where(col(Chapter.serial).in_(to_delete))
                )
                for serial in to_delete:
                    file = existing[serial].content_file
                    ctx.files.resolve(file).unlink(True)

            sess.commit()
