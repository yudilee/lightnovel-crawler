from functools import lru_cache
from typing import Any, Iterable, List, Optional, TypeVar

from sqlalchemy import delete as sa_delete
from sqlalchemy import update as sa_update
from sqlalchemy.orm import aliased
from sqlmodel import (Session, and_, asc, case, cast, col, desc, func, literal,
                      or_, select, true)

from ...context import ctx
from ...dao import Job, User
from ...dao.enums import (JobPriority, JobStatus, JobType, OutputFormat,
                          UserRole)
from ...dao.tier import JOB_PRIORITY_LEVEL
from ...exceptions import ServerErrors
from ...server.models.pagination import Paginated
from ...utils.time_utils import current_timestamp
from .utils import sa_select_children, sa_select_parents

T = TypeVar('T')

job_alias = aliased(Job)
job_status_type = Job.__table__.c.status.type  # type: ignore
job_success_literal = cast(literal(JobStatus.SUCCESSFUL.name), job_status_type)
job_running_literal = cast(literal(JobStatus.RUNNING.name), job_status_type)


class JobService:
    def __init__(self) -> None:
        pass

    # -------------------------------------------------------------------------
    #                               GET Jobs
    # -------------------------------------------------------------------------
    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        *,
        user_id: Optional[str] = None,
        job_type: Optional[JobType] = None,
        priority: Optional[JobPriority] = None,
        status: Optional[JobStatus] = None,
        is_done: Optional[bool] = None,
        parent_job_id: Optional[str] = None,
    ) -> Paginated[Job]:
        with ctx.db.session() as sess:
            stmt = select(Job)
            cnt = select(func.count()).select_from(Job)

            # Apply filters
            conditions: List[Any] = []
            if user_id is not None:
                conditions.append(Job.user_id == user_id)
            if parent_job_id is not None:
                conditions.append(Job.parent_job_id == parent_job_id)
            else:
                conditions.append(col(Job.parent_job_id).is_(None))
            if job_type is not None:
                conditions.append(Job.type == job_type)
            if status is not None:
                conditions.append(Job.status == status)
            if is_done is not None:
                conditions.append(col(Job.is_done).is_(true()))
            if priority is not None:
                conditions.append(Job.priority == priority)

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            if parent_job_id is not None:
                stmt = stmt.order_by(asc(Job.created_at))
            else:
                stmt = stmt.order_by(desc(Job.created_at))

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

    def get(self, job_id: str) -> Job:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise ServerErrors.no_such_job
            return job

    def get_user_id(self, job_id: str) -> Optional[str]:
        with ctx.db.session() as sess:
            stmt = select(Job.user_id).where(Job.id == job_id)
            return sess.exec(stmt).first()

    def verify_access(self, user: User, job_id: str) -> str:
        user_id = self.get_user_id(job_id)
        if not user_id:
            raise ServerErrors.no_such_job
        if user_id != user.id and user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
        return user_id

    def get_children_ids(self, parent_job_id: str) -> Iterable[str]:
        with ctx.db.session() as sess:
            stmt = select(Job.id).where(Job.parent_job_id == parent_job_id)
            return sess.exec(stmt).all()

    def get_children(self, parent_job_id: str) -> Iterable[Job]:
        with ctx.db.session() as sess:
            stmt = select(Job).where(Job.parent_job_id == parent_job_id)
            return sess.exec(stmt).all()

    # -------------------------------------------------------------------------
    #                              CANCEL Jobs
    # -------------------------------------------------------------------------

    def cancel(self, job_id: str, who: str = 'admin') -> None:
        with ctx.db.session() as sess:
            self._cancel_down(sess, job_id, True)
            self._success(sess, job_id)
            self._update(
                sess,
                job_id,
                status=JobStatus.CANCELED,
                error=f'Canceled by {who}',
            )
            sess.commit()

    # -------------------------------------------------------------------------
    #                              DELETE Jobs
    # -------------------------------------------------------------------------
    def delete(self, job_id: str) -> None:
        with ctx.db.session() as sess:
            result = sess.exec(
                select(Job.done, Job.total)
                .where(Job.id == job_id)
            ).first()
            if not result:
                return
            done, total = result

            self._update_up(
                sess,
                job_id=job_id,
                done=Job.done - done,
                total=Job.total - total,
            )

            sa_deps = sa_select_children(job_id, True)
            sess.exec(
                sa_delete(Job)
                .where(col(Job.id).in_(sa_deps))
            )

            sess.commit()

    # -------------------------------------------------------------------------
    #                              CREATE Jobs
    # -------------------------------------------------------------------------
    def fetch_novel(
        self,
        user: User,
        url: str,
        *,
        full: bool = False,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        ctx.sources.get_crawler(url)  # validate
        data.update({
            'url': url
        })
        novel = ctx.novels.find_by_url(url)
        if novel:
            data['novel_id'] = novel.id
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.FULL_NOVEL if full else JobType.NOVEL,
        )

    def fetch_many_novels(
        self,
        user: User,
        *urls: str,
        full: bool = False,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update({
            'urls': urls
        })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.FULL_NOVEL_BATCH if full else JobType.NOVEL_BATCH,
        )

    def fetch_volume(
        self,
        user: User,
        volume_id: str,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        volume = ctx.volumes.get(volume_id)
        data.update({
            'volume_id': volume_id,
            'volume_serial': volume.serial,
        })
        if not data.get('novel_title'):
            novel = ctx.novels.get(volume.novel_id)
            data.update({
                'novel_id': novel.id,
                'novel_title': novel.title,
            })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.VOLUME,
        )

    def fetch_many_volumes(
        self,
        user: User,
        *volume_ids: str,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update({
            'volume_ids': volume_ids,
        })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.VOLUME_BATCH,
        )

    def fetch_chapter(
        self,
        user: User,
        chapter_id: str,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        chapter = ctx.chapters.get(chapter_id)
        data.update({
            'chapter_id': chapter_id,
            'chapter_serial': chapter.serial,
        })
        if not data.get('novel_title'):
            novel = ctx.novels.get(chapter.novel_id)
            data.update({
                'novel_id': novel.id,
                'novel_title': novel.title,
            })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.CHAPTER,
        )

    def fetch_many_chapters(
        self,
        user: User,
        *chapter_ids: str,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update({
            'chapter_ids': chapter_ids,
        })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.CHAPTER_BATCH,
        )

    def fetch_image(
        self,
        user: User,
        image_id: str,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        image = ctx.images.get(image_id)
        data.update({
            'image_id': image_id,
            'url': image.url,
        })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.IMAGE,
        )

    def fetch_many_images(
        self,
        user: User,
        *image_ids: str,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update({
            'image_ids': image_ids,
        })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.IMAGE_BATCH,
        )

    def make_artifact(
        self,
        user: User,
        novel_id: str,
        format: OutputFormat,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update({
            'novel_id': novel_id,
            'format': format,
        })
        if not data.get('novel_title'):
            novel = ctx.novels.get(novel_id)
            data.update({
                'novel_title': novel.title,
            })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.ARTIFACT,
        )

    def make_many_artifacts(
        self,
        user: User,
        novel_id: str,
        *formats: OutputFormat,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update({
            'novel_id': novel_id,
            'formats': formats,
        })
        if not data.get('novel_title'):
            novel = ctx.novels.get(novel_id)
            data.update({
                'novel_title': novel.title,
            })
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.ARTIFACT_BATCH,
        )

    # -------------------------------------------------------------------------
    #                            Internal Methods
    # -------------------------------------------------------------------------
    def _create(
        self,
        user: User,
        type: JobType,
        data: dict,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
    ) -> Job:
        with ctx.db.session() as sess:
            job = Job(
                type=type,
                extra=data,
                user_id=user.id,
                depends_on=depends_on,
                parent_job_id=parent_id,
                priority=JOB_PRIORITY_LEVEL[user.tier],
            )
            sess.add(job)

            self._update_up(
                sess,
                job.id,
                total=Job.total + 1,
            )

            sess.commit()
            sess.refresh(job)
            return job

    @lru_cache
    def _get_root(self, job_id: str) -> Optional[str]:
        with ctx.db.session() as sess:
            sa_pars = sa_select_parents(job_id)
            return sess.exec(
                select(Job.id)
                .where(col(Job.id).in_(sa_pars))
                .where(col(Job.parent_job_id).is_(None))
                .limit(1)
            ).first()

    def _pending(self, artifact: bool, skip_job_ids: Iterable[str]) -> Optional[Job]:
        with ctx.db.session() as sess:
            stmt = select(Job)

            stmt = stmt.outerjoin(job_alias, col(job_alias.id) == Job.depends_on)
            stmt = stmt.where(
                or_(
                    col(Job.depends_on).is_(None),
                    col(job_alias.is_done).is_(true())
                )
            )

            stmt = stmt.where(
                or_(
                    Job.status == JobStatus.PENDING,
                    and_(
                        Job.status == JobStatus.RUNNING,
                        Job.done == 0,
                    )
                ),
            )

            if artifact:
                stmt = stmt.where(Job.type == JobType.ARTIFACT)
            else:
                stmt = stmt.where(Job.type != JobType.ARTIFACT)
                stmt = stmt.where(col(Job.id).not_in(skip_job_ids))

            stmt = stmt.order_by(
                desc(Job.priority),
                asc(Job.created_at),
            )

            return sess.exec(stmt.limit(1)).first()

    def _update(self, sess: Session, job_id: str, **values) -> None:
        sess.exec(
            sa_update(Job)
            .where(col(Job.id) == job_id)
            .values(**values)
        )

    def _update_up(
        self,
        sess: Session,
        job_id: str,
        done=Job.done,
        total=Job.total,
        inclusive: bool = False,
    ) -> None:
        now = current_timestamp()
        sa_total = case(
            (total < 1, 1),
            else_=total,
        )
        sa_done = case(
            (done <= sa_total, done),
            else_=sa_total,
        )
        sa_is_done = sa_done == sa_total
        sa_started_at = case(
            (sa_is_done, func.coalesce(Job.started_at, now)),
            else_=Job.started_at
        )
        sa_finished_at = case(
            (sa_is_done, func.coalesce(Job.finished_at, now)),
            else_=Job.finished_at
        )
        sa_status = case(
            (sa_is_done, job_success_literal),
            else_=job_running_literal
        )

        sa_pars = sa_select_parents(job_id, inclusive)
        sess.exec(
            sa_update(Job)
            .where(col(Job.id).in_(sa_pars))
            .where(col(Job.is_done).is_not(true()))
            .values(
                done=sa_done,
                total=sa_total,
                status=sa_status,
                is_done=sa_is_done,
                started_at=sa_started_at,
                finished_at=sa_finished_at,
            )
        )

    def _cancel_down(self, sess: Session, job_id: str, inclusive=False) -> None:
        now = current_timestamp()
        sa_deps = sa_select_children(job_id, inclusive)
        sess.exec(
            sa_update(Job)
            .where(
                col(Job.id).in_(sa_deps),
                col(Job.is_done).is_not(true()),
            )
            .values(
                is_done=True,
                # done=Job.total,
                status=JobStatus.CANCELED,
                error='Canceled by one of the parent',
                started_at=func.coalesce(Job.started_at, now),
                finished_at=func.coalesce(Job.finished_at, now),
            )
        )

    def _increment_up(self, sess: Session, job_id: str, step: int = 1) -> None:
        self._update_up(
            sess,
            job_id=job_id,
            inclusive=True,
            done=Job.done + step,
        )

    def _success(self, sess: Session, job_id: str) -> None:
        pending = sess.exec(
            select(Job.total - Job.done)
            .where(Job.id == job_id)
        ).one()
        self._increment_up(sess, job_id, pending)

    def _fail(self, sess: Session, job_id: str, reason: str) -> None:
        self._cancel_down(sess, job_id)
        self._success(sess, job_id)
        self._update(
            sess,
            job_id,
            error=reason,
            status=JobStatus.FAILED,
        )
