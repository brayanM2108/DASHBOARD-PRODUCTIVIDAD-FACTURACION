from ..core.exceptions.auth import InvalidCredentialsException, UserAlreadyExist
from ..repositories.user_repository import UserRepository
from ..core.security import verify_password, hash_password, create_access_token


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, username: str, password: str) -> str | None:
        user = self.user_repo.get_by_username(username)
        if not user:
            raise InvalidCredentialsException()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        return create_access_token(user.username)

    def register(self, username: str, password: str):
        existing = self.user_repo.get_by_username(username)
        if existing:
            raise UserAlreadyExist()
        hashed = hash_password(password)
        user = self.user_repo.create(username=username, hashed_password=hashed)
        token = create_access_token(user.username)
        return user, token
