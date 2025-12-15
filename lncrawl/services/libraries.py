from typing import Optional

import sqlmodel as sa

from ..context import ctx
from ..dao import Library, LibraryNovel, Novel, User, UserRole
from ..exceptions import ServerErrors
from ..server.models.library import LibraryOwner, LibrarySummary
from ..server.models.pagination import Paginated


def _owner_info(user: User) -> LibraryOwner:
    return LibraryOwner(
        id=user.id,
        name=user.name,
    )


class LibraryService:
    def __init__(self) -> None:
        pass

    def _get_library(self, sess, library_id: str) -> Library:
        library = sess.get(Library, library_id)
        if not library:
            raise ServerErrors.no_such_library
        return library

    def _ensure_owner(self, library: Library, user: User):
        if library.user_id != user.id and user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden

    def _ensure_visible(self, library: Library, user: User):
        if library.is_public or library.user_id == user.id or user.role == UserRole.ADMIN:
            return
        raise ServerErrors.forbidden

    def list_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[LibrarySummary]:
        with ctx.db.session() as sess:
            stmt = (
                sa.select(
                    Library,
                    User,
                    sa.func.count(LibraryNovel.novel_id).label("novel_count"),
                )
                .join(User, User.id == Library.user_id)
                .join(LibraryNovel, LibraryNovel.library_id == Library.id, isouter=True)
                .group_by(Library.id, User.id)
                .order_by(sa.desc(Library.updated_at))
                .offset(offset)
                .limit(limit)
            )
            cnt = sa.select(sa.func.count()).select_from(Library)

            rows = sess.exec(stmt).all()
            total = sess.exec(cnt).one()

            items = [
                LibrarySummary(
                    library=Library(**row[0].model_dump()),
                    owner=_owner_info(row[1]),
                    novel_count=row[2],
                )
                for row in rows
            ]

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=items,
            )

    def list_user(
        self,
        user_id: str,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[LibrarySummary]:
        with ctx.db.session() as sess:
            stmt = (
                sa.select(
                    Library,
                    User,
                    sa.func.count(LibraryNovel.novel_id).label("novel_count"),
                )
                .join(User, User.id == Library.user_id)
                .join(LibraryNovel, LibraryNovel.library_id == Library.id, isouter=True)
                .where(Library.user_id == user_id)
                .group_by(Library.id, User.id)
                .order_by(sa.desc(Library.updated_at))
                .offset(offset)
                .limit(limit)
            )
            cnt = (
                sa.select(sa.func.count())
                .select_from(Library)
                .where(Library.user_id == user_id)
            )

            rows = sess.exec(stmt).all()
            total = sess.exec(cnt).one()

            items = [
                LibrarySummary(
                    library=Library(**row[0].model_dump()),
                    owner=_owner_info(row[1]),
                    novel_count=row[2],
                )
                for row in rows
            ]

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=items,
            )

    def list_public(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[LibrarySummary]:
        with ctx.db.session() as sess:
            stmt = (
                sa.select(
                    Library,
                    User,
                    sa.func.count(LibraryNovel.novel_id).label("novel_count"),
                )
                .join(User, User.id == Library.user_id)
                .join(LibraryNovel, LibraryNovel.library_id == Library.id, isouter=True)
                .where(Library.is_public.is_(True))
                .group_by(Library.id, User.id)
                .order_by(sa.desc(Library.updated_at))
                .offset(offset)
                .limit(limit)
            )
            cnt = (
                sa.select(sa.func.count())
                .select_from(Library)
                .where(Library.is_public.is_(True))
            )

            rows = sess.exec(stmt).all()
            total = sess.exec(cnt).one()

            items = [
                LibrarySummary(
                    library=Library(**row[0].model_dump()),
                    owner=_owner_info(row[1]),
                    novel_count=row[2],
                )
                for row in rows
            ]

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=items,
            )

    def create(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        is_public: bool = False,
    ) -> Library:
        with ctx.db.session() as sess:
            library = Library(
                user_id=user_id,
                name=name.strip(),
                description=description.strip() if description else None,
                is_public=is_public,
            )
            sess.add(library)
            sess.commit()
            sess.refresh(library)
            return library

    def update(
        self,
        library_id: str,
        user: User,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Library:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)

            if name is not None:
                library.name = name.strip()
            if description is not None:
                library.description = description.strip() if description else None
            if is_public is not None:
                library.is_public = is_public

            sess.commit()
            sess.refresh(library)
            return library

    def delete(self, library_id: str, user: User) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)
            sess.delete(library)
            sess.commit()
            return True

    def get(
        self,
        library_id: str,
        user: User,
    ) -> Library:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_visible(library, user)
            return library

    def list_novels(
        self,
        library_id: str,
        user: User,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[Novel]:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_visible(library, user)

            cnt = (
                sa.select(sa.func.count())
                .select_from(LibraryNovel)
                .where(LibraryNovel.library_id == library_id)
            )
            stmt = (
                sa.select(Novel)
                .join(LibraryNovel, LibraryNovel.novel_id == Novel.id)
                .where(LibraryNovel.library_id == library_id)
                .order_by(sa.desc(Novel.updated_at))
                .offset(offset)
                .limit(limit)
            )

            total = sess.exec(cnt).one()
            items = sess.exec(stmt).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def add_novel(self, library_id: str, user: User, novel_id: str) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)

            novel = sess.get(Novel, novel_id)
            if not novel:
                raise ServerErrors.no_such_novel

            exists_stmt = sa.select(LibraryNovel).where(
                sa.and_(
                    LibraryNovel.library_id == library_id,
                    LibraryNovel.novel_id == novel_id,
                )
            )
            existing = sess.exec(exists_stmt).first()
            if existing:
                return True

            link = LibraryNovel(library_id=library_id, novel_id=novel_id)
            sess.add(link)
            sess.commit()
            return True

    def remove_novel(self, library_id: str, user: User, novel_id: str) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)

            link = sess.get(LibraryNovel, {"library_id": library_id, "novel_id": novel_id})
            if not link:
                return True

            sess.delete(link)
            sess.commit()
            return True
