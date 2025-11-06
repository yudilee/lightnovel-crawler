from typing import Optional

from sqlmodel import desc, func, select

from ..context import ctx
from ..dao import Artifact, User
from ..dao.enums import OutputFormat, UserRole
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated


class ArtifactService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        novel_id: Optional[str] = None,
        format: Optional[OutputFormat] = None,
    ) -> Paginated[Artifact]:
        with ctx.db.session() as sess:
            stmt = select(Artifact)

            # Apply filters
            if novel_id:
                stmt = stmt.where(Artifact.novel_id == novel_id)
            if user_id:
                stmt = stmt.where(Artifact.user_id == user_id)
            if job_id:
                stmt = stmt.where(Artifact.job_id == job_id)
            if format:
                stmt = stmt.where(Artifact.format == format)

            # Apply sorting
            stmt = stmt.order_by(desc(Artifact.updated_at))

            total = sess.exec(select(func.count()).select_from(Artifact)).one()
            items = sess.exec(stmt.offset(offset).limit(limit)).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def get(self, artifact_id: str) -> Artifact:
        with ctx.db.session() as sess:
            artifact = sess.get(Artifact, artifact_id)
            if not artifact:
                raise ServerErrors.no_such_artifact
            return artifact

    def delete(self, artifact_id: str, user: User) -> bool:
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
        with ctx.db.session() as sess:
            artifact = sess.get(Artifact, artifact_id)
            if not artifact:
                raise ServerErrors.no_such_artifact
            ctx.files.resolve(artifact.output_file).unlink(True)
            sess.delete(artifact)
            sess.commit()
            return True

    def get_latest(self, novel_id: str, format: str) -> Optional[Artifact]:
        with ctx.db.session() as sess:
            artifact = sess.exec(
                select(Artifact)
                .where(Artifact.novel_id == novel_id)
                .where(Artifact.format == format)
                .order_by(desc(Artifact.updated_at))
                .limit(1)
            ).first()
            return artifact
