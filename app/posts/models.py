from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from .. import db


class PostCategory(str, Enum):
    NEWS = "news"
    PUBLICATION = "publication"
    TECH = "tech"
    OTHER = "other"


class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, server_default=func.current_timestamp(), nullable=False)
    category: Mapped[PostCategory] = mapped_column(
        SqlEnum(PostCategory, name="post_category", native_enum=False,
                values_callable=lambda enum: [item.value for item in enum]),
        default=PostCategory.OTHER, server_default=text("'other'"), nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("1"), nullable=False)
    author: Mapped[str] = mapped_column(String(20), default="Anonymous", server_default=text("'Anonymous'"), nullable=False)

    def __repr__(self):
        return f"<Post {self.id}: {self.title!r}>"
