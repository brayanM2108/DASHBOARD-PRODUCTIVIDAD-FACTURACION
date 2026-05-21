from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, hash_password, create_access_token

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, db: Session, username: str, password: str) -> str | None:
        user = self.user_repo.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return create_access_token(user.username)

    def register(self, db: Session, username: str, password: str):
        existing = self.user_repo.get_by_username(db, username)
        if existing:
            return None
        hashed = hash_password(password)
        user = self.user_repo.create(db, username=username, hashed_password=hashed)
        token = create_access_token(user.username)
        return user, token