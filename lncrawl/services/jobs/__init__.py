from typing import Any, List, Optional

from pydantic import HttpUrl
from sqlalchemy import delete as sa_delete
from sqlalchemy import update as sa_update
from sqlmodel import and_, asc, case, col, desc, func, select, true

from ...context import ctx
from ...dao import Job, User
from ...dao.enums import (JobPriority, JobStatus, JobType, OutputFormat,
                          UserRole)
from ...exceptions import ServerErrors
from ...server.models.job import JobProgress
from ...server.models.pagination import Paginated
from ...server.tier import JOB_PRIORITY_LEVEL
from ...utils.time_utils import current_timestamp


def sa_parent_update(job_id: str):
    pars = (
        select(Job.parent_job_id)
        .where(Job.id == job_id)
        .cte('ancestor', recursive=True)
    )
    pars = pars.union_all(
        select(Job.parent_job_id)
        .where(Job.id == pars.c.parent_job_id)
    )
    return (
        sa_update(Job)
        .where(
            col(Job.id).in_(select(pars.c.id)),
        )
    )


def sa_select_children(job_id: str):
    deps = (
        select(Job.id)
        .where(Job.id == job_id)
        .cte("descendends", recursive=True)
    )
    deps = deps.union_all(
        select(Job.id)
        .where(Job.parent_job_id == deps.c.id)
    )
    return select(deps.c.id)


class JobService:
    def __init__(self) -> None:
        pass

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

    def list_pending(self, limit: int = 5) -> List[Job]:
        with ctx.db.session() as sess:
            stmt = select(Job)
            stmt = stmt.where(col(Job.is_done).is_(False))
            stmt = stmt.order_by(
                desc(Job.priority),
                asc(Job.created_at),
            )
            stmt = stmt.limit(limit)
            jobs = sess.exec(stmt).all()
            return list(jobs)

    def get(self, job_id: str) -> Job:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise ServerErrors.no_such_job
            return job

    def calculate_progress(
        self,
        job_id: str,
        skip_cache: bool = False
    ) -> JobProgress:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise ServerErrors.no_such_job
            deps = (
                select(Job.id, Job.is_done)
                .where(Job.id == job_id)
                .cte("deps", recursive=True)
            )
            deps = deps.union_all(
                select(Job.id, Job.is_done)
                .where(Job.parent_job_id == deps.c.id)
            )
            stmt = select(
                func.count().label("total"),
                func.sum(
                    case(
                        (deps.c.is_done.is_(true()), 1),
                        else_=0
                    )
                ).label("done"),
            )
            total, done = sess.exec(stmt).one()
            job.extra['total'] = total
            job.extra['done'] = done
            sess.commit()

        progress = JobProgress(
            job_id=job_id,
            done=done,
            total=total,
            percent=(100 * done) // total,
        )
        return progress

    def cancel(self, user: User, job_id: str) -> None:
        with ctx.db.session() as sess:
            # verify job exists
            job = sess.get(Job, job_id)
            if not job or job.is_done:
                return

            # verify user access
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise ServerErrors.forbidden
            who = 'user' if job.user_id == user.id else 'admin'

            # cancel job with the subtree
            now = current_timestamp()
            deps = (
                select(Job.id)
                .where(Job.id == job_id)
                .cte("descendends", recursive=True)
            )
            deps = deps.union_all(
                select(Job.id)
                .where(Job.parent_job_id == deps.c.id)
            )
            update_result = sess.exec(
                sa_update(Job)
                .where(
                    col(Job.id).in_(select(deps.c.id)),
                    col(Job.is_done).is_(False),
                )
                .values(
                    is_done=True,
                    done=Job.total,
                    status=JobStatus.CANCELED,
                    error=f'Canceled by {who}',
                    started_at=func.coalesce(Job.started_at, now),
                    finished_at=func.coalesce(Job.finished_at, now),
                )
            )
            total_updated = update_result.rowcount

            # recursively update parents
            sess.exec(
                sa_parent_update(job_id)
                .values(
                    total=Job.total - total_updated,
                )
            )

            sess.commit()

    def delete(self, user: User, job_id: str) -> None:
        with ctx.db.session() as sess:
            # verify job exists
            job = sess.get(Job, job_id)
            if not job:
                return

            # verify user access
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise ServerErrors.forbidden

            # delete job with the subtree
            deps = (
                select(Job.id)
                .where(Job.id == job_id)
                .cte("descendends", recursive=True)
            )
            deps = deps.union_all(
                select(Job.id)
                .where(Job.parent_job_id == deps.c.id)
            )
            delete_result = sess.exec(
                sa_delete(Job)
                .where(
                    col(Job.id).in_(select(deps.c.id))
                )
            )
            total_removed = delete_result.rowcount

            # recursively update parents
            sess.exec(
                sa_parent_update(job_id)
                .values(
                    total=Job.total - total_removed,
                )
            )

            sess.commit()

    def create_job(
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
            sess.commit()
            sess.refresh(job)
            return job

    def fetch_novel(
        self,
        user: User,
        url: HttpUrl,
        *,
        full: bool = False,
        parent_id: Optional[str] = None,
    ) -> Job:
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
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
        return self.create_job(
            user=user,
            parent_id=parent_id,
            type=JobType.ARTIFACT_BATCH,
            data={'novel_id': novel_id, 'formats': formats},
        )
