
from flask import render_template, request, redirect, url_for, session, flash, make_response
from . import users_bp

DEMO_USERNAME = "student"
DEMO_PASSWORD = "flask123"


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == DEMO_USERNAME and password == DEMO_PASSWORD:
            session["username"] = username
            flash("Вхід успішний. Вітаємо!", "success")
            return redirect(url_for("users.profile"))
        flash("Неправильне ім’я користувача або пароль.", "error")
    return render_template("user/login.html")


@users_bp.route("/profile", methods=["GET", "POST"])
def profile():
    username = session.get("username")
    if not username:
        flash("Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))

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
    return render_template("user/profile.html", username=username, cookies=cookies,
                           theme=request.cookies.get("profile_theme", "light"))


@users_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви вийшли із системи.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/profile/theme/<theme>")
def profile_theme(theme):
    if "username" not in session:
        flash("Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))
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
