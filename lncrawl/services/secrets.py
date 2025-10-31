from typing import Any, List, Optional

from sqlmodel import and_, col, func, select

from ..context import ctx
from ..dao import Secret
from ..dao.enums import SecretType
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated
from ..utils.text_tools import text_decrypt, text_encrypt


class SecretService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str = '',
        type: Optional[SecretType] = None,
    ) -> Paginated[Secret]:
        with ctx.db.session() as sess:
            stmt = select(Secret)
            cnt = select(func.count()).select_from(Secret)

            # Apply filter
            conditions: List[Any] = []
            if search:
                conditions.append(col(Secret.name).ilike(f"%{search}%"))
            if type is not None:
                conditions.append(Secret.type == type)

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(col(Secret.created_at).desc())

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

    def get(self, secret_id: str) -> Secret:
        with ctx.db.session() as sess:
            secret = sess.get(Secret, secret_id)
            if not secret:
                raise ServerErrors.no_such_secret
            return secret

    def add(self, type: SecretType, name: str, value: str, ) -> Secret:
        key = ctx.config.app.secret_key
        encrypted = text_encrypt(value.encode(), key)
        with ctx.db.session() as sess:
            secret = Secret(
                type=type,
                name=name,
                value=encrypted,
            )
            sess.add(secret)
            sess.commit()
            return secret

    def update(
        self,
        secret_id: str,
        name: Optional[str],
        value: Optional[str],
    ) -> Secret:
        with ctx.db.session() as sess:
            secret = sess.get(Secret, secret_id)
            if not secret:
                raise ServerErrors.no_such_secret
            if name is not None:
                secret.name = name
            if value is not None:
                key = ctx.config.app.secret_key
                secret.value = text_encrypt(value.encode(), key)
            sess.commit()
            return secret

    def delete(self, name: str) -> None:
        with ctx.db.session() as sess:
            secret = sess.get(Secret, name)
            if secret:
                sess.delete(secret)
                sess.commit()

    def get_random_value(self, name: str) -> Optional[str]:
        '''Gets a decrypted random secret value matching the name'''
        with ctx.db.session() as sess:
            secret = sess.exec(
                select(Secret.value)
                .where(Secret.name == name)
                .order_by(func.random())
                .limit(1)
            ).first()
            if not secret:
                return None
            key = ctx.config.app.secret_key
            plain = text_decrypt(secret, key)
            return plain.decode()
