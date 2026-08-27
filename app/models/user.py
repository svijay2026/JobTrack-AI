from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.db.base import Base


class User(Base):
    """
    User database model representing the `users` table.
    Stores account credentials, profile info, and account status.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"
