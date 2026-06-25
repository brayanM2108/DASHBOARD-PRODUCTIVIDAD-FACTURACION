from ..core.exceptions.auth import (
    InvalidCredentialsException,
    UserAlreadyExist,
    InvalidTokenException,
    EmailAlreadyExist, UserNotActivate, ForbiddenException
)
from ..core.exceptions.business import ValidationException
from ..repositories.user_repository import UserRepository
from ..core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_refresh_token,
    decode_token,
)
from ..utils.password_generator import generate_temporary_password
import logging

logger = logging.getLogger(__name__)
MIN_PASSWORD_LENGTH = 8


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, email: str, password: str) -> tuple:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        if not user.is_active:
            raise UserNotActivate()

        access_token = create_access_token(user.email, user.username, user.role, user.is_active)
        refresh_token = create_refresh_token(user.email, user.username, user.role, user.is_active)

        token_hash = hash_refresh_token(refresh_token)
        logger.info("Token generated for user %s", user.email)

        self.user_repo.update_refresh_token(user, token_hash)

        return user, access_token, refresh_token

    def register(
        self,
        email: str,
        document: str,
        username: str,
        password: str,
        role: str | None = None,
    ) -> tuple:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise EmailAlreadyExist()

        existing_username = self.user_repo.get_by_username(username)
        if existing_username:
            raise UserAlreadyExist()

        hashed = hash_password(password)
        user = self.user_repo.create(
            username=username,
            email=email,
            document=document,
            hashed_password=hashed,
            role=None,
        )

        access_token = create_access_token(user.email, user.username, user.role, user.is_active)
        refresh_token = create_refresh_token(user.email, user.username, user.role, user.is_active)

        self.user_repo.update_refresh_token(
            user, hash_refresh_token(refresh_token)
        )
        self.user_repo.db.commit()
        self.user_repo.db.refresh(user)

        return user, access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple:
        logger.debug("Refresh token request received")
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            logger.warning("Invalid or non-refresh token used")
            raise InvalidTokenException()

        email = payload.get("sub")
        if not email:
            logger.warning("Refresh token missing sub claim")
            raise InvalidTokenException()

        user = self.user_repo.get_by_email(email)
        if not user or not user.refresh_token_hash:
            logger.warning("User not found or no stored refresh hash for %s", email)
            raise InvalidTokenException()

        if not verify_refresh_token(refresh_token, user.refresh_token_hash):
            logger.warning("Refresh token hash mismatch for %s", email)
            raise InvalidTokenException()

        if not user.is_active:
            raise InvalidTokenException()
        new_access_token = create_access_token(user.email, user.username, user.role, user.is_active)
        new_refresh_token = create_refresh_token(user.email, user.username, user.role, user.is_active)

        self.user_repo.update_refresh_token(
            user, hash_refresh_token(new_refresh_token)
        )

        logger.info("Refresh successful for %s", email)
        return user, new_access_token, new_refresh_token

    def revoke_refresh_token(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)
        if user:
            self.user_repo.update_refresh_token(user, None)

    def change_password(self, user, new_password: str) -> None:
        if len(new_password) < MIN_PASSWORD_LENGTH:
            raise ValidationException(
                message=f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres",
                status_code=400,
                error_code="WEAK_PASSWORD",
            )
        hashed = hash_password(new_password)
        self.user_repo.reset_password(user, hashed)

    def admin_reset_password(self, admin_user, target_user_id: int, new_password: str | None = None) -> dict:
        if admin_user.role != "ADMIN":
            raise ForbiddenException()

        target = self.user_repo.get_by_id(target_user_id)
        if not target:
            raise UserNotActivate()

        password = new_password or generate_temporary_password()
        hashed = hash_password(password)
        self.user_repo.admin_reset_password(target, hashed)
        return {"user_id": target.id, "temp_password": password}
