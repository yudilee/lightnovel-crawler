from functools import cached_property
from typing import Any, List, Optional

from sqlmodel import and_, col, func, select

from ..context import ctx
from ..dao import Secret
from ..exceptions import ServerErrors
from ..server.models.crawler import LoginData
from ..server.models.pagination import Paginated
from ..utils.text_tools import generate_uuid, text_decrypt, text_encrypt
from ..utils.url_tools import extract_host

SECRET_KEY_ID = '--server-secret-key--'


class SecretService:
    def __init__(self) -> None:
        pass

    @cached_property
    def secret_key(self) -> bytes:
        with ctx.db.session() as sess:
            secret = sess.get(Secret, SECRET_KEY_ID)
            if secret:
                return secret.value

        value = generate_uuid().encode()
        admin = ctx.users.get_admin()
        secret = Secret(
            name=SECRET_KEY_ID,
            user_id=admin.id,
            value=value,
        )
        with ctx.db.session() as sess:
            sess.add(secret)
            sess.commit()
        return value

    def _decrypt(self, value: bytes) -> str:
        return text_decrypt(value, self.secret_key).decode()

    def _encrypt(self, value: str) -> bytes:
        return text_encrypt(value.encode(), self.secret_key)

    def list(
        self,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
        search: str = '',
    ) -> Paginated[Secret]:
        with ctx.db.session() as sess:
            stmt = select(Secret)
            cnt = select(func.count()).select_from(Secret)

            # Apply filter
            conditions: List[Any] = []
            conditions.append(Secret.user_id == user_id)
            conditions.append(Secret.name != SECRET_KEY_ID)
            if search:
                conditions.append(col(Secret.name).ilike(f"%{search}%"))

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

    def add(
        self,
        user_id: str,
        name: str,
        value: str,
    ) -> Secret:
        if name == SECRET_KEY_ID:
            raise ServerErrors.invalid_input
        with ctx.db.session() as sess:
            secret = Secret(
                name=name,
                user_id=user_id,
                value=self._encrypt(value),
            )
            sess.add(secret)
            sess.commit()
            return secret

    def get(self, user_id: str, name: str) -> Secret:
        if name == SECRET_KEY_ID:
            raise ServerErrors.no_such_secret
        with ctx.db.session() as sess:
            secret = sess.get(Secret, name)
            if not secret or secret.user_id != user_id:
                raise ServerErrors.no_such_secret
            return secret

    def delete(self, user_id: str, name: str) -> None:
        if name == SECRET_KEY_ID:
            return
        with ctx.db.session() as sess:
            secret = sess.get(Secret, name)
            if not secret or secret.user_id != user_id:
                return
            sess.delete(secret)
            sess.commit()

    def get_value(self, user_id: str, name: str) -> Optional[str]:
        try:
            secret = self.get(user_id, name)
            return self._decrypt(secret.value)
        except Exception:
            return None

    def add_login(self, user_id: str, url: str, login: LoginData) -> None:
        host = extract_host(url)
        if not host:
            raise ServerErrors.invalid_url
        self.add(user_id, host, login.model_dump_json())

    def get_login(self, user_id: str, url: str) -> Optional[LoginData]:
        host = extract_host(url)
        value = self.get_value(user_id, host)
        if not value:
            return None
        return LoginData.model_validate_json(value)
