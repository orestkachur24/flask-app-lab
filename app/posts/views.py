from datetime import datetime

from flask import abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from .. import db
from . import posts_bp
from .forms import PostForm
from .models import Post, PostCategory


@posts_bp.get("")
def list_posts():
    posts = db.session.scalars(select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc(), Post.id.desc())).all()
    return render_template("posts/all_posts.html", posts=posts)


@posts_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data.strip(), content=form.content.data.strip(),
                    is_active=form.enabled.data, posted=form.publish_date.data or datetime.utcnow(),
                    category=PostCategory(form.category.data), author=session.get("username", "Anonymous")[:20])
        db.session.add(post)
        db.session.commit()
        flash("Пост створено.", "success")
        return redirect(url_for("posts.detail_post", post_id=post.id))
    return render_template("posts/add_post.html", form=form, heading="Створити пост")


@posts_bp.get("/<int:post_id>")
def detail_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    return render_template("posts/detail_post.html", post=post)


@posts_bp.route("/<int:post_id>/update", methods=["GET", "POST"])
def update_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    form = PostForm()
    if not form.is_submitted():
        form.title.data = post.title
        form.content.data = post.content
        form.enabled.data = post.is_active
        form.publish_date.data = post.posted
        form.category.data = post.category.value
    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.content = form.content.data.strip()
        post.is_active = form.enabled.data
        post.posted = form.publish_date.data or post.posted
        post.category = PostCategory(form.category.data)
        db.session.commit()
        flash("Пост оновлено.", "success")
        return redirect(url_for("posts.detail_post", post_id=post.id))
    return render_template("posts/add_post.html", form=form, heading="Редагувати пост", post=post)


@posts_bp.route("/<int:post_id>/delete", methods=["GET", "POST"])
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        flash("Пост видалено.", "success")
        return redirect(url_for("posts.list_posts"))
    return render_template("posts/delete_confirm.html", post=post)
