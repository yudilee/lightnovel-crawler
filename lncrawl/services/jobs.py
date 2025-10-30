from typing import Any, List, Optional

from pydantic import HttpUrl
from sqlmodel import and_, asc, desc, func, or_, select

from ..context import ctx
from ..dao import Job, User
from ..dao.enums import JobPriority, JobStatus, JobType, OutputFormat, UserRole
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated
from ..server.tier import JOB_PRIORITY_LEVEL


class JobService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        *,
        sort_by: str = "created_at",
        order: str = "desc",
        user_id: Optional[str] = None,
        job_type: Optional[JobType] = None,
        priority: Optional[JobPriority] = None,
        status: Optional[JobStatus] = None,
    ) -> Paginated[Job]:
        with ctx.db.session() as sess:
            stmt = select(Job)
            cnt = select(func.count()).select_from(Job)

            # Apply filters
            conditions: List[Any] = []
            if user_id is not None:
                conditions.append(Job.user_id == user_id)
            if job_type is not None:
                conditions.append(Job.type == job_type)
            if status is not None:
                conditions.append(Job.status == status)
            if priority is not None:
                conditions.append(Job.priority == priority)

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            sort_column = getattr(Job, sort_by, None)
            if sort_column is None:
                raise ServerErrors.sort_column_is_none
            order_fn = desc if order == "desc" else asc
            stmt = stmt.order_by(order_fn(sort_column))

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
            stmt = stmt.where(
                or_(
                    Job.status == JobStatus.PENDING,
                    Job.status == JobStatus.RUNNING,
                )
            )
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

    def delete(self, job_id: str, user: User) -> bool:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                return True
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise ServerErrors.forbidden
            sess.delete(job)
            sess.commit()
            return True

    def cancel(self, job_id: str, user: User) -> bool:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job or job.is_completed:
                return True
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise ServerErrors.forbidden
            who = 'user' if job.user_id == user.id else 'admin'
            job.error = f'Canceled by {who}'
            job.status = JobStatus.CANCELED
            sess.commit()
            return True

    def fetch_novel(self, user: User, url: HttpUrl, full: bool = False) -> Job:
        with ctx.db.session() as sess:
            job = Job(
                user_id=user.id,
                priority=JOB_PRIORITY_LEVEL[user.tier],
                type=JobType.FULL_NOVEL if full else JobType.NOVEL,
                extra={'url': url.encoded_string()},
            )
            sess.add(job)
            sess.commit()
            sess.refresh(job)
            return job

    def fetch_chapters(self, user: User, *chapter_ids: str) -> Job:
        if not chapter_ids:
            raise ServerErrors.no_chapters
        with ctx.db.session() as sess:
            if len(chapter_ids) == 1:
                job = Job(
                    user_id=user.id,
                    priority=JOB_PRIORITY_LEVEL[user.tier],
                    type=JobType.CHAPTER,
                    extra={'chapter_id': chapter_ids[0]},
                )
            else:
                job = Job(
                    user_id=user.id,
                    priority=JOB_PRIORITY_LEVEL[user.tier],
                    type=JobType.BATCH_CHAPTERS,
                    extra={'chapter_ids': chapter_ids},
                )
            sess.add(job)
            sess.commit()
            sess.refresh(job)
            return job

    def fetch_image(self, user: User, image_id: str) -> Job:
        with ctx.db.session() as sess:
            job = Job(
                user_id=user.id,
                priority=JOB_PRIORITY_LEVEL[user.tier],
                type=JobType.CHAPTER,
                extra={'image_id': image_id},
            )
            sess.add(job)
            sess.commit()
            sess.refresh(job)
            return job

    def make_artifact(self, user: User, novel_id: str, format: OutputFormat) -> Job:
        with ctx.db.session() as sess:
            job = Job(
                user_id=user.id,
                priority=JOB_PRIORITY_LEVEL[user.tier],
                type=JobType.ARTIFACT,
                extra={'novel_id': novel_id, 'format': format},
            )
            sess.add(job)
            sess.commit()
            sess.refresh(job)
            return job
