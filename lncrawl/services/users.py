import base64
import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import sqlmodel as sa
from jose import jwt
from passlib.context import CryptContext

from ..context import ctx
from ..dao import NotificationItem, User, UserRole, UserTier, VerifiedEmail
from ..exceptions import ServerErrors
from ..server.models.pagination import Paginated
from ..server.models.user import (CreateRequest, LoginRequest,
                                  PasswordUpdateRequest, SignupRequest,
                                  UpdateRequest)
from ..utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self) -> None:
        self._admin: Optional[User] = None
        self._passlib = CryptContext(
            schemes=['argon2'],
            deprecated='auto',
        )

    def _hash(self, plain_password: str) -> str:
        return self._passlib.hash(plain_password)

    def _check(self, plain: str, hashed: str) -> bool:
        return self._passlib.verify(plain, hashed)

    def setup_admin(self) -> None:
        email = ctx.config.db.admin_email
        password = ctx.config.db.admin_password
        with ctx.db.session() as sess:
            user = sess.exec(
                sa.select(User).where(User.email == email).limit(1)
            ).first()
            if not user:
                logger.info('Adding admin user')
                user = User(
                    email=email,
                    password=self._hash(password),
                    name="Server Admin",
                    role=UserRole.ADMIN,
                    tier=UserTier.VIP,
                )
                sess.add(user)
            else:
                logger.info('Updating admin user')
                user.password = self._hash(password)
                user.role = UserRole.ADMIN
                user.tier = UserTier.VIP
                user.is_active = True
            sess.commit()
        self._admin = user

    def encode_token(
        self,
        payload: Dict[str, Any],
        expiry_minutes: Optional[int] = None,
    ) -> str:
        key = ctx.config.server.token_secret
        algorithm = ctx.config.server.token_algo
        default_expiry = ctx.config.server.token_expiry
        minutes = expiry_minutes if expiry_minutes else default_expiry
        payload['exp'] = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        return jwt.encode(payload, key, algorithm)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            key = ctx.config.server.token_secret
            algorithm = ctx.config.server.token_algo
            return jwt.decode(token, key, algorithm)
        except Exception as e:
            raise ServerErrors.unauthorized from e

    def generate_token(
        self,
        user: User,
        expiry_minutes: Optional[int] = None,
        **payload,
    ) -> str:
        payload = {
            'sub': user.id,
            'scopes': [user.role, user.tier],
        }
        return self.encode_token(payload, expiry_minutes)

    def verify_token(self, token: str, required_scopes: List[str] = []) -> User:
        payload = self.decode_token(token)
        user_id = payload.get('sub')
        token_scopes = payload.get('scopes', [])
        if not user_id:
            raise ServerErrors.unauthorized
        if any(scope not in token_scopes for scope in required_scopes):
            raise ServerErrors.forbidden
        return self.get(user_id)

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Paginated[User]:
        with ctx.db.session() as sess:
            stmt = sa.select(User)
            cnt = sa.select(sa.func.count()).select_from(User)

            # Apply filters
            conditions: List[Any] = []
            if search:
                q = f'%{search}%'
                conditions.append(
                    sa.or_(
                        sa.col(User.name).ilike(q),
                        sa.col(User.email).ilike(q),
                        sa.cast(User.role, sa.String).ilike(q),
                        sa.cast(User.tier, sa.String).ilike(q),
                    )
                )

            if conditions:
                cnt = cnt.where(*conditions)
                stmt = stmt.where(*conditions)

            # Apply sorting
            stmt = stmt.order_by(sa.asc(User.created_at))

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

    def get_admin(self) -> User:
        if not self._admin:
            self.setup_admin()
            assert self._admin
        return self._admin

    def get(self, user_id: str) -> User:
        with ctx.db.session() as sess:
            user = sess.get(User, user_id)
            if not user:
                raise ServerErrors.no_such_user
            return user

    def verify(self, creds: LoginRequest) -> User:
        with ctx.db.session() as sess:
            q = sa.select(User).where(User.email == creds.email)
            user = sess.exec(q).first()
            if not user:
                raise ServerErrors.no_such_user
            if not self._check(creds.password, user.password):
                raise ServerErrors.unauthorized
            if not user.is_active:
                raise ServerErrors.inactive_user
            return user

    def create(self, body: CreateRequest) -> User:
        with ctx.db.session() as sess:
            q = sa.select(sa.func.count()).where(User.email == body.email)
            if sess.exec(q).one() != 0:
                raise ServerErrors.user_exists
            user = User(
                name=body.name,
                email=body.email,
                role=body.role,
                tier=body.tier,
                referrer_id=body.referrer_id,
                password=self._hash(body.password),
                extra=dict(
                    email_alerts={
                        NotificationItem.NOVEL_SUCCESS: 1,
                        NotificationItem.ARTIFACT_SUCCESS: 1,
                    },
                )
            )
            sess.add(user)
            sess.commit()
            sess.refresh(user)
            return user

    def update(self, user_id: str, body: UpdateRequest) -> None:
        with ctx.db.session() as sess:
            user = sess.get(User, user_id)
            if not user:
                raise ServerErrors.no_such_user

            if body.name is not None:
                user.name = body.name
            if body.password is not None:
                user.password = self._hash(body.password)
            if body.role is not None:
                user.role = body.role
            if body.tier is not None:
                user.tier = body.tier
            if body.is_active is not None:
                user.is_active = body.is_active
            if body.extra is not None:
                extra = dict(user.extra)
                extra.update(body.extra)
                user.extra = extra

            sess.commit()

    def change_password(self, user: User, body: PasswordUpdateRequest) -> None:
        if not self._check(body.old_password, user.password):
            raise ServerErrors.unauthorized
        request = UpdateRequest(password=body.new_password)
        self.update(user.id, request)

    def remove(self, user_id: str) -> None:
        with ctx.db.session() as sess:
            user = sess.get(User, user_id)
            if user:
                sess.delete(user)
                sess.commit()

    def is_verified(self, email: str) -> bool:
        with ctx.db.session() as sess:
            verified = sess.get(VerifiedEmail, email)
            return bool(verified)

    def set_verified(self, email: str) -> None:
        if self.is_verified(email):
            return

        with ctx.db.session() as sess:
            user = sess.exec(
                sa.select(User).where(User.email == email)
            ).first()
            if not user:
                raise ServerErrors.no_such_user

            row = VerifiedEmail(email=email)
            sess.add(row)

            if 'email_alerts' not in user.extra:
                extra = dict(user.extra)
                extra['email_alerts'] = {
                    NotificationItem.NOVEL_SUCCESS: 1,
                    NotificationItem.ARTIFACT_SUCCESS: 1,
                }
                user.extra = extra

            sess.commit()

    def send_otp(self, email: str) -> str:
        with ctx.db.session() as sess:
            verified = sess.get(VerifiedEmail, email)
            if verified:
                raise ServerErrors.email_already_verified

        otp = str(secrets.randbelow(1000000)).zfill(6)
        ctx.mail.send_otp(email, otp)

        return self.encode_token({
            'otp': self._hash(otp),
            'email': email,
        }, 5)

    def verify_otp(self, token: str, input_otp: str) -> None:
        payload = self.decode_token(token)
        email = payload.get('email')
        if not email:
            raise ServerErrors.not_found

        hashed_otp = payload.get('otp') or ''
        if not self._check(input_otp, hashed_otp):
            raise ServerErrors.wrong_otp

        with ctx.db.session() as sess:
            row = VerifiedEmail(email=email)
            sess.add(row)
            sess.commit()

    def send_password_reset_link(self, email: str) -> None:
        with ctx.db.session() as sess:
            q = sa.select(User).where(User.email == email)
            user = sess.exec(q).first()
            if not user:
                raise ServerErrors.no_such_user
            if not user.is_active:
                raise ServerErrors.inactive_user

        token = self.generate_token(user, 5)
        base_url = ctx.config.server.base_url
        link = f'{base_url}/reset-password?token={token}'
        ctx.mail.send_reset_password_link(email, link)

    def generate_user_token(self, user: User) -> str:
        user_id = user.id
        time = current_timestamp()

        t_bytes = time.to_bytes(8, 'little')
        id_bytes = uuid.UUID(user_id).bytes

        t_key = hashlib.sha3_256(t_bytes).digest()[:16]
        encrypted_id = bytes(x ^ y for x, y in zip(id_bytes, t_key))

        encrypted = t_bytes + encrypted_id

        encoded = base64.urlsafe_b64encode(encrypted)
        token = encoded.decode('ascii')
        return token

    def verify_user_token(self, token: str) -> str:
        try:
            encoded = token.encode('ascii')
            encrypted = base64.urlsafe_b64decode(encoded)

            t_bytes = encrypted[:8]
            t_key = hashlib.sha3_256(t_bytes).digest()[:16]

            encrypted_id = encrypted[8:]
            id_bytes = bytes(x ^ y for x, y in zip(encrypted_id, t_key))

            time = int.from_bytes(t_bytes, 'little')
            user_id = str(uuid.UUID(bytes=id_bytes))
        except Exception as e:
            raise ServerErrors.token_invalid from e

        exp = ctx.config.server.token_expiry * (60 * 1000)
        if time + exp < current_timestamp():
            raise ServerErrors.token_expired

        return user_id

    def signup(self, body: SignupRequest):
        referrer_id = self.verify_user_token(body.referrer)
        request = CreateRequest(
            name=body.name,
            email=body.email,
            password=body.password,
            referrer_id=referrer_id,
        )
        return self.create(request)
