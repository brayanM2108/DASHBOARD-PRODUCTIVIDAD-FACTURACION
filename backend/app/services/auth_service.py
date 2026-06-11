from prompt_toolkit import document

from ..core.exceptions.auth import (
    InvalidCredentialsException,
    UserAlreadyExist,
    InvalidTokenException,
    EmailAlreadyExist
)
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


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, email: str, password: str) -> tuple:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        access_token = create_access_token(user.email, user.username, user.role)
        refresh_token = create_refresh_token(user.email, user.username, user.role)

        print(f"[AUTH] Token generado: {refresh_token[:30]}...")
        token_hash = hash_refresh_token(refresh_token)
        print(f"[AUTH] Hash calculado: {token_hash[:20]}...")
        
        self.user_repo.update_refresh_token(user, token_hash)
        print(f"[AUTH] Hash guardado en BD para {user.email}")

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
            role=role,
        )

        access_token = create_access_token(user.email, user.username, user.role)
        refresh_token = create_refresh_token(user.email, user.username, user.role)

        self.user_repo.update_refresh_token(
            user, hash_refresh_token(refresh_token)
        )
        self.user_repo.db.commit()
        self.user_repo.db.refresh(user)

        return user, access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple:
        print(f"[BACKEND AUTH] Refresh token recibido: {refresh_token[:20]}...")
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            print(f"[BACKEND AUTH] Token inválido o no es refresh: payload={payload}")
            raise InvalidTokenException()

        email = payload.get("sub")
        if not email:
            print("[BACKEND AUTH] Token no tiene sub")
            raise InvalidTokenException()

        user = self.user_repo.get_by_email(email)
        if not user or not user.refresh_token_hash:
            print(f"[BACKEND AUTH] Usuario no encontrado o sin refresh_token_hash: user={user}")
            raise InvalidTokenException()

        incoming_hash = hash_refresh_token(refresh_token)
        stored_hash = user.refresh_token_hash
        print(f"[BACKEND AUTH] Hash calculado: {incoming_hash[:20]}...")
        print(f"[BACKEND AUTH] Hash en BD: {stored_hash[:20]}...")
        print(f"[BACKEND AUTH] ¿Coinciden? {incoming_hash == stored_hash}")

        if not verify_refresh_token(refresh_token, user.refresh_token_hash):
            print(f"[BACKEND AUTH] Refresh token no coincide con el hash en BD")
            raise InvalidTokenException()

        new_access_token = create_access_token(user.email, user.username, user.role)
        new_refresh_token = create_refresh_token(user.email, user.username, user.role)

        self.user_repo.update_refresh_token(
            user, hash_refresh_token(new_refresh_token)
        )

        print(f"[BACKEND AUTH] Refresh exitoso para {email}")
        return user, new_access_token, new_refresh_token

    def revoke_refresh_token(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)
        if user:
            self.user_repo.update_refresh_token(user, None)
