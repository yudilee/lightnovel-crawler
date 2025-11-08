from typing import Any, List, Optional

from pydantic import HttpUrl
from sqlalchemy import delete as sa_delete
from sqlalchemy import update as sa_update
from sqlmodel import and_, asc, case, col, func, select, true

from ...context import ctx
from ...dao import Job, User
from ...dao.enums import (JobPriority, JobStatus, JobType, OutputFormat,
                          UserRole)
from ...dao.tier import JOB_PRIORITY_LEVEL
from ...exceptions import ServerErrors
from ...server.models.pagination import Paginated
from ...utils.time_utils import current_timestamp
from .utils import sa_select_children, sa_select_parents


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
            stmt = stmt.order_by(asc(Job.created_at))

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

    # -------------------------------------------------------------------------
    #                              CANCEL Jobs
    # -------------------------------------------------------------------------

    def cancel(self, user: User, job_id: str, reason: Optional[str] = None) -> None:
        with ctx.db.session() as sess:
            # verify job exists
            job = sess.get(Job, job_id)
            if not job or job.is_done:
                return

            # verify user access
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise ServerErrors.forbidden

            if not reason:
                who = 'user' if job.user_id == user.id else 'admin'
                reason = f'Canceled by {who}'

            # selectors
            sa_pars = sa_select_parents(job_id)
            sa_deps = sa_select_children(job_id)

            # recursively update parents
            now = current_timestamp()
            sa_done = Job.done + job.total
            sa_is_done = sa_done == Job.total
            sa_started_at = func.coalesce(Job.started_at, now)
            sa_finished_at = func.coalesce(Job.finished_at, now)
            sess.exec(
                sa_update(Job)
                .where(col(Job.id).in_(sa_pars))
                .values(
                    done=sa_done,
                    is_done=sa_is_done,
                    error=case((sa_is_done, reason), else_=Job.error),
                    status=case((sa_is_done, JobStatus.CANCELED), else_=Job.status),
                    started_at=case((sa_is_done, sa_started_at), else_=Job.started_at),
                    finished_at=case((sa_is_done, sa_finished_at), else_=Job.finished_at),
                )
            )

            # cancel job and all children
            sess.exec(
                sa_update(Job)
                .where(
                    col(Job.id).in_(sa_deps),
                    col(Job.is_done).is_not(true()),
                )
                .values(
                    error=reason,
                    is_done=True,
                    done=Job.total,
                    started_at=sa_started_at,
                    finished_at=sa_finished_at,
                    status=JobStatus.CANCELED,
                )
            )

            sess.commit()

    # -------------------------------------------------------------------------
    #                              DELETE Jobs
    # -------------------------------------------------------------------------
    def delete(self, user: User, job_id: str) -> None:
        with ctx.db.session() as sess:
            # verify job exists
            job = sess.get(Job, job_id)
            if not job:
                return

            # verify user access
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise ServerErrors.forbidden

            # selectors
            sa_pars = sa_select_parents(job_id)
            sa_deps = sa_select_children(job_id)

            # parameters
            now = current_timestamp()
            sa_done = Job.done - job.done
            sa_total = Job.total - job.total
            sa_is_done = sa_done == sa_total
            sa_started_at = func.coalesce(Job.started_at, now)
            sa_finished_at = func.coalesce(Job.finished_at, now)

            # recursively update parents
            sess.exec(
                sa_update(Job)
                .where(col(Job.id).in_(sa_pars))
                .values(
                    done=sa_done,
                    total=sa_total,
                    is_done=sa_is_done,
                    status=case((sa_is_done, JobStatus.SUCCESS), else_=Job.status),
                    started_at=case((sa_is_done, sa_started_at), else_=Job.started_at),
                    finished_at=case((sa_is_done, sa_finished_at), else_=Job.finished_at),
                )
            )

            # delete job with the subtree
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
        url: HttpUrl,
        *,
        full: bool = False,
        parent_id: Optional[str] = None,
    ) -> Job:
        if not url.host:
            raise ServerErrors.invalid_url
        ctx.sources.get_crawler(url.encoded_string())
        return self._create(
            user=user,
            parent_id=parent_id,
            data={'url': url.encoded_string()},
            type=JobType.FULL_NOVEL if full else JobType.NOVEL,
        )

    def fetch_many_novels(
        self,
        user: User,
        *urls: HttpUrl,
        full: bool = False,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            data={'url': [url.encoded_string() for url in urls]},
            type=JobType.FULL_NOVEL_BATCH if full else JobType.NOVEL_BATCH,
        )

    def fetch_volume(
        self,
        user: User,
        volume_id: str,
        *,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.VOLUME,
            data={'volume_id': volume_id},
        )

    def fetch_many_volumes(
        self,
        user: User,
        *volume_ids: str,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.VOLUME_BATCH,
            data={'volume_ids': volume_ids},
        )

    def fetch_chapter(
        self,
        user: User,
        chapter_id: str,
        *,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.CHAPTER,
            data={'chapter_id': chapter_id},
        )

    def fetch_many_chapters(
        self,
        user: User,
        *chapter_ids: str,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.CHAPTER_BATCH,
            data={'chapter_ids': chapter_ids},
        )

    def fetch_image(
        self,
        user: User,
        image_id: str,
        *,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.IMAGE,
            data={'image_id': image_id},
        )

    def fetch_many_images(
        self,
        user: User,
        *image_ids: str,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.IMAGE_BATCH,
            data={'image_ids': image_ids},
        )

    def make_artifact(
        self,
        user: User,
        novel_id: str,
        format: OutputFormat,
        *,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.ARTIFACT,
            data={'novel_id': novel_id, 'format': format},
        )

    def make_many_artifacts(
        self,
        user: User,
        novel_id: str,
        *formats: OutputFormat,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self._create(
            user=user,
            parent_id=parent_id,
            type=JobType.ARTIFACT_BATCH,
            data={'novel_id': novel_id, 'formats': formats},
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
    ) -> Job:
        with ctx.db.session() as sess:
            job = Job(
                type=type,
                extra=data,
                user_id=user.id,
                parent_job_id=parent_id,
                priority=JOB_PRIORITY_LEVEL[user.tier],
            )
            sess.add(job)

            # recursively update parents
            sa_pars = sa_select_parents(job.id)
            sess.exec(
                sa_update(Job)
                .where(col(Job.id).in_(sa_pars))
                .values(
                    total=Job.total + 1,
                    # error=None,
                    # is_done=False,
                    # finished_at=None,
                    # status=JobStatus.PENDING,
                )
            )

            sess.commit()
            sess.refresh(job)
            return job

    def _update(self, job_id: str, **values) -> None:
        with ctx.db.session() as sess:
            sess.exec(
                sa_update(Job)
                .where(col(Job.id) == job_id)
                .values(**values)
            )
            sess.commit()
