from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from flask_bcrypt import check_password_hash
from werkzeug.security import check_password_hash as check_werkzeug_password_hash

from .. import bcrypt, db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        if self.password.startswith("!"):
            return False
        if self.password.startswith(("scrypt:", "pbkdf2:")):
            return check_werkzeug_password_hash(self.password, raw_password)
        return check_password_hash(self.password, raw_password)

    def __repr__(self) -> str:
        return f"<User {self.username!r}>"


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
