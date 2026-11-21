from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, String, Table, Text, Column, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import db


post_tags = db.Table(
    "post_tags",
    Column("post_id", ForeignKey("posts.id", name="fk_post_tags_post_id_posts"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", name="fk_post_tags_tag_id_tags"), primary_key=True),
)


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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_posts_user_id_users"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")

    def __repr__(self):
        return f"<Post {self.id}: {self.title!r}>"


from ..users.models import User  # noqa: E402,F401
from .tags import Tag  # noqa: E402,F401
