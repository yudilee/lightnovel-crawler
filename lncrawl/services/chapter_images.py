from typing import Any, Dict, List, Optional

from sqlalchemy import delete as sa_delete
from sqlalchemy import insert as sa_insert
from sqlmodel import and_, func, select

from ..context import ctx
from ..dao import ChapterImage
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated
from ..utils.url_tools import normalize_url


class ChapterImageService:
    def __init__(self) -> None:
        pass

    def count(self, novel_id: str) -> int:
        with ctx.db.session() as sess:
            stmt = select(func.count()).select_from(ChapterImage)
            stmt = stmt.where(ChapterImage.novel_id == novel_id)
            return sess.exec(stmt).one()

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str = '',
        novel_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        is_crawled: Optional[bool] = None,
    ) -> Paginated[ChapterImage]:
        with ctx.db.session() as sess:
            stmt = select(ChapterImage)
            cnt = select(func.count()).select_from(ChapterImage)

            # Apply filters
            conditions: List[Any] = []

            if search:
                q = f"%{normalize_url(search)}%"
                conditions.append(ChapterImage.url.like(q))  # type: ignore
            if novel_id:
                conditions.append(ChapterImage.novel_id == novel_id)
            if chapter_id:
                conditions.append(ChapterImage.chapter_id == chapter_id)
            if is_crawled:
                conditions.append(ChapterImage.crawled.is_(True))  # type: ignore

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

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

    def get(self, image_id: str) -> ChapterImage:
        with ctx.db.session() as sess:
            image = sess.get(ChapterImage, image_id)
            if not image:
                raise ServerErrors.no_such_file
            return image

    def delete(self, image_id: str) -> bool:
        with ctx.db.session() as sess:
            image = sess.get(ChapterImage, image_id)
            if not image:
                return True
            ctx.files.resolve(image.image_file).unlink(True)
            sess.delete(image)
            sess.commit()
            return True

    def sync(self, novel_id: str, chapter_id: str, images: Dict[str, str]):
        with ctx.db.session() as sess:
            existing = {
                img.id: img
                for img in sess.exec(
                    select(ChapterImage)
                    .where(ChapterImage.chapter_id == chapter_id)
                ).all()
            }

            wk = set(images.keys())
            ek = set(existing.keys())
            to_insert = wk - ek
            to_delete = ek - wk

            if to_insert:
                sess.exec(
                    sa_insert(ChapterImage),
                    params=[
                        ChapterImage(
                            id=id,
                            url=images[id],
                            novel_id=novel_id,
                            chapter_id=chapter_id,
                        ).model_dump()
                        for id in to_insert
                    ]
                )
            if to_delete:
                sess.exec(
                    sa_delete(ChapterImage)
                    .where(
                        ChapterImage.id.in_(to_delete),  # type: ignore
                    )
                )
                for id in to_delete:
                    file = existing[id].image_file
                    ctx.files.resolve(file).unlink(True)

            sess.commit()
