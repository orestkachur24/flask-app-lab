from flask import current_app, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from . import users_bp
from .forms import LoginForm, RegistrationForm
from .models import User


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.strip(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Реєстрація успішна. Ви увійшли в систему.", "success")
            return redirect(url_for("users.account"))
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Could not register user")
            flash("Не вдалося зберегти користувача. Спробуйте ще раз.", "error")
    return render_template("user/register.html", form=form)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))
    form = LoginForm()
    if form.validate_on_submit():
        identity = form.username.data.strip()
        user = db.session.execute(
            select(User).where(or_(User.username == identity, User.email == identity.lower()))
        ).scalar_one_or_none()
        if user and user.check_password(form.password.data):
            # Upgrade passwords made by Lab8's Werkzeug hash to Bcrypt after successful login.
            if user.password.startswith(("scrypt:", "pbkdf2:")):
                user.set_password(form.password.data)
                db.session.commit()
            login_user(user)
            flash(f"Вітаємо, {user.username}! Вхід успішний.", "success")
            return redirect(url_for("users.account"))
        flash("Неправильне ім’я користувача/email або пароль.", "error")
    return render_template("user/login.html", form=form)


@users_bp.route("/account")
@login_required
def account():
    return render_template("user/account.html", user=current_user)


@users_bp.route("/all")
@login_required
def all_users():
    users = db.session.scalars(select(User).order_by(User.id)).all()
    return render_template("user/all_users.html", users=users, count=len(users))


@users_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Ви успішно вийшли із системи.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        action = request.form.get("action")
        key = request.form.get("key", "").strip()
        if action == "add":
            value = request.form.get("value", "")
            try:
                max_age = max(0, int(request.form.get("days", "30"))) * 86400
            except ValueError:
                max_age = 30 * 86400
            if not key:
                flash("Вкажіть ключ cookie.", "error")
            else:
                response = make_response(redirect(url_for("users.profile")))
                response.set_cookie(key, value, max_age=max_age, httponly=True, samesite="Lax")
                flash(f"Cookie «{key}» додано.", "success")
                return response
        elif action == "delete_one":
            if key:
                response = make_response(redirect(url_for("users.profile")))
                response.delete_cookie(key)
                flash(f"Cookie «{key}» видалено.", "success")
                return response
            flash("Вкажіть ключ cookie для видалення.", "error")
        elif action == "delete_all":
            response = make_response(redirect(url_for("users.profile")))
            for cookie_key in request.cookies:
                if cookie_key != "session":
                    response.delete_cookie(cookie_key)
            flash("Усі користувацькі cookie видалено.", "success")
            return response

    cookies = {key: value for key, value in request.cookies.items() if key != "session"}
    return render_template("user/profile.html", username=current_user.username, cookies=cookies,
                           theme=request.cookies.get("profile_theme", "light"))


@users_bp.route("/profile/theme/<theme>")
@login_required
def profile_theme(theme):
    if theme not in {"light", "dark"}:
        theme = "light"
    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie("profile_theme", theme, max_age=365 * 86400, httponly=True, samesite="Lax")
    flash("Колірну схему оновлено.", "success")
    return response


@users_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", default=None, type=int)
    return render_template("user/hi.html", name=name, age=age)


@users_bp.route("/admin")
def admin():
    return redirect(url_for("users.greetings", name="administrator", age=45))
