from sqlalchemy.orm import Session
from ..models import User

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(
        self,
        username: str,
        email: str,
        document: str,
        hashed_password: str,
        is_active: bool = True,
        role: str | None = None,
    ) -> User:
        user = User(
            username=username,
            email=email,
            document=document,
            hashed_password=hashed_password,
            is_active=is_active,
            role=role,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def update_refresh_token(self, user, refresh_token_hash):
        user.refresh_token_hash = refresh_token_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_all(self) -> list[User]:
        return self.db.query(User).all()

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
