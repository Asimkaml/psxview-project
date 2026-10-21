from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).one_or_none()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).one_or_none()

    def create(self, *, email: str, username: str, display_name: str | None, password_hash: str) -> User:
        user = User(
            email=email,
            username=username,
            display_name=display_name,
            password_hash=password_hash,
        )
        self.db.add(user)
        self.db.flush()
        return user
