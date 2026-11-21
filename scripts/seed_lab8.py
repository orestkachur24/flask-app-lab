"""Create the example users, tags, and five posts required for Lab8."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app import create_app, db
from app.posts.models import Post, PostCategory
from app.posts.tags import Tag
from app.users.models import User


app = create_app("development")

with app.app_context():
    user1 = db.session.scalar(select(User).where(User.username == "user1"))
    if user1 is None:
        user1 = db.session.scalar(select(User).order_by(User.id).limit(1))
        if user1 is None:
            user1 = User(username="user1", email="user1@example.test", password="")
            db.session.add(user1)
        else:
            user1.username = "user1"
            user1.email = "user1@example.test"
        user1.set_password("lab8-password-1")

    user2 = db.session.scalar(select(User).where(User.username == "user2"))
    if user2 is None:
        user2 = User(username="user2", email="user2@example.test", password="")
        user2.set_password("lab8-password-2")
        db.session.add(user2)
    db.session.flush()

    tags = {}
    for name in ("orm", "database", "performance"):
        tag = db.session.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            db.session.add(tag)
        tags[name] = tag
    db.session.flush()

    posts = db.session.scalars(select(Post).order_by(Post.id)).all()
    if posts:
        posts[0].user = user1
        posts[0].tags = [tags["orm"], tags["database"]]
    if len(posts) > 1:
        posts[1].user = user2
        posts[1].tags = [tags["database"], tags["performance"]]

    examples = [
        ("SQLAlchemy relationships", "One-to-many and many-to-many examples.", user1, ["orm", "database"]),
        ("Tagging posts", "A tag can belong to several posts.", user2, ["orm"]),
        ("Query loading", "Compare lazy and eager loading strategies.", user2, ["performance", "database"]),
    ]
    for title, content, author, tag_names in examples:
        post = db.session.scalar(select(Post).where(Post.title == title))
        if post is None:
            post = Post(title=title, content=content, user=author, category=PostCategory.TECH)
            db.session.add(post)
        post.user = author
        post.tags = [tags[name] for name in tag_names]

    db.session.commit()
    for user in db.session.scalars(select(User).order_by(User.id)):
        print(user.id, user.username, [post.title for post in user.posts])
    for tag in db.session.scalars(select(Tag).order_by(Tag.name)):
        print(tag.name, [post.title for post in tag.posts])
