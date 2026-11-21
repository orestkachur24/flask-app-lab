from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import db
from .models import post_tags


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    posts: Mapped[list["Post"]] = relationship(secondary=post_tags, back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag {self.name!r}>"
