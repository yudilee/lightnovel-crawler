from typing import Any, List, Optional

from pydantic import HttpUrl
from sqlmodel import and_, asc, desc, func, or_, select

from ..context import ctx
from ..dao import Artifact, Job, Novel, User
from ..dao.enums import JobPriority, JobStatus, RunState, UserRole
from ..exceptions import ServerErrors
from ..server.models.job import JobDetail
from ..server.models.pagination import Paginated
from ..server.tier import JOB_PRIORITY_LEVEL


class JobService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        user_id: Optional[str] = None,
        novel_id: Optional[str] = None,
        priority: Optional[JobPriority] = None,
        status: Optional[JobStatus] = None,
        run_state: Optional[RunState] = None,
    ) -> Paginated[Job]:
        with ctx.db.session() as sess:
            stmt = select(Job)
            cnt = select(func.count()).select_from(Job)

            # Apply filters
            conditions: List[Any] = []
            if user_id is not None:
                conditions.append(Job.user_id == user_id)
            if novel_id is not None:
                conditions.append(Job.novel_id == novel_id)
            if status is not None:
                conditions.append(Job.status == status)
            if run_state is not None:
                conditions.append(Job.run_state == run_state)
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

    def pending_jobs(self, limit: int = 5) -> List[Job]:
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

    async def create(self, url: HttpUrl, user: User):
        novel = ctx.novels.get_by_url(url)
        with ctx.db.session() as sess:
            # create the job
            job = Job(
                user_id=user.id,
                novel_id=novel.id,
                url=novel.url,
                priority=JOB_PRIORITY_LEVEL[user.tier],
            )
            sess.add(job)
            sess.commit()
            sess.refresh(job)
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
            if not job or job.status == JobStatus.COMPLETED:
                return True
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise ServerErrors.forbidden
            who = 'user' if job.user_id == user.id else 'admin'
            job.error = f'Canceled by {who}'
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.CANCELED
            sess.add(job)
            sess.commit()
            return True

    def get(self, job_id: str) -> JobDetail:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise ServerErrors.no_such_job
            user = sess.get_one(User, job.user_id)
            novel = sess.get(Novel, job.novel_id)
            artifacts = sess.exec(
                select(Artifact).where(Artifact.job_id == job.id)
            ).all()
            return JobDetail(
                job=job,
                user=user,
                novel=novel,
                artifacts=list(artifacts),
            )

    def get_artifacts(self, job_id: str) -> List[Artifact]:
        with ctx.db.session() as sess:
            q = select(Artifact).where(Artifact.job_id == job_id)
            return list(sess.exec(q).all())

    def get_novel(self, job_id: str) -> Novel:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise ServerErrors.no_such_job
            novel = sess.get(Novel, job.novel_id)
            if not novel:
                raise ServerErrors.no_such_novel
            return novel
