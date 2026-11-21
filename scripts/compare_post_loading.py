"""Compare lazy relationship loads with joinedload/selectinload.

Run in separate processes so each mode starts with a fresh ORM identity map:
    python scripts/compare_post_loading.py lazy
    python scripts/compare_post_loading.py eager
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import event, select
from sqlalchemy.orm import joinedload, selectinload

from app import create_app, db
from app.posts.models import Post


mode = sys.argv[1] if len(sys.argv) > 1 else "lazy"
if mode not in {"lazy", "eager"}:
    raise SystemExit("Choose either 'lazy' or 'eager'.")

app = create_app("development")
select_count = 0


def count_selects(connection, cursor, statement, parameters, context, executemany):
    global select_count
    if statement.lstrip().upper().startswith("SELECT"):
        select_count += 1


with app.app_context():
    db.session.remove()
    event.listen(db.engine, "before_cursor_execute", count_selects)
    stmt = select(Post).order_by(Post.id.desc())
    if mode == "eager":
        stmt = stmt.options(joinedload(Post.user), selectinload(Post.tags))
    posts = db.session.scalars(stmt).unique().all()
    for post in posts:
        print(post.title, post.user.username, [tag.name for tag in post.tags])
    event.remove(db.engine, "before_cursor_execute", count_selects)
    print(f"Mode: {mode}; posts: {len(posts)}; SELECT statements: {select_count}")
    db.session.remove()
