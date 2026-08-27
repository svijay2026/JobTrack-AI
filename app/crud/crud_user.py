from typing import Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser:
    """
    CRUD operations for User database entity.
    Encapsulates all database query logic for users.
    """

    def get(self, db: Session, id: int) -> Optional[User]:
        """Fetch user by primary key ID."""
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Fetch user by unique email address."""
        return db.query(User).filter(User.email == email.lower().strip()).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """
        Creates a new user record with hashed password.
        """
        db_obj = User(
            email=obj_in.email.lower().strip(),
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name.strip(),
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Validates email and password credentials.
        Returns User object if valid, None otherwise.
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update(
        self,
        db: Session,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        """
        Updates user attributes (e.g. name, password).
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Global CRUD instance
user_crud = CRUDUser()
