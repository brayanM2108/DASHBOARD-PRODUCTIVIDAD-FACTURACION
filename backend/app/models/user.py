from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(100), unique=True, index=True, nullable=False)

    username = Column(String(100), unique=True, index=True, nullable=False)

    document = Column(String(100), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)

    must_change_password = Column(Boolean, default=True)

    role = Column(String(50))

    refresh_token_hash = Column(String(255), nullable=True)
