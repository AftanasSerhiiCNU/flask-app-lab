from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response,
    current_app
)
from . import users_bp


def get_session_cookie_name():
    return current_app.config.get("SESSION_COOKIE_NAME", "session")


@users_bp.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, type=int)

    return render_template(
        "users/hi.html",
        name=name,
        age=age,
        title="Привітання"
    )


@users_bp.route("/admin")
def admin():
    to_url = url_for(
        "users.greetings",
        name="administrator",
        age=45
    )

    return redirect(to_url)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "admin123":
            session.clear()
            session["username"] = username
            flash("Вхід виконано успішно!", "success")
            return redirect(url_for("users.profile"))

        flash("Неправильний логін або пароль!", "error")
        return redirect(url_for("users.login"))

    return render_template("users/login.html", title="Вхід")


@users_bp.route("/profile")
def profile():
    username = session.get("username")

    if not username:
        flash("Помилка! Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))

    cookies = {
        key: value
        for key, value in request.cookies.items()
        if key != get_session_cookie_name()
    }

    theme = request.cookies.get("theme", "light")

    if theme not in ("light", "dark"):
        theme = "light"

    return render_template(
        "users/profile.html",
        username=username,
        cookies=cookies,
        theme=theme,
        title="Профіль"
    )


@users_bp.route("/theme/<theme>", methods=["POST"])
def change_theme(theme):
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "error")
        return redirect(url_for("users.login"))

    if theme not in ("light", "dark"):
        flash("Невідома кольорова схема!", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))

    response.set_cookie(
        "theme",
        theme,
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="Lax"
    )

    flash("Тему успішно змінено!", "success")

    return response


@users_bp.route("/cookies/add", methods=["POST"])
def add_cookie():
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "error")
        return redirect(url_for("users.login"))

    key = request.form.get("key", "").strip()
    value = request.form.get("value", "")
    duration = request.form.get("duration", "")

    if not key or not value or not duration:
        flash("Заповніть усі поля!", "error")
        return redirect(url_for("users.profile"))

    if key == get_session_cookie_name():
        flash("Не можна змінювати системну cookie сесії!", "error")
        return redirect(url_for("users.profile"))

    try:
        minutes = int(duration)

        if not 1 <= minutes <= 525600:
            raise ValueError

    except ValueError:
        flash("Вкажіть термін від 1 до 525600 хвилин!", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))

    try:
        response.set_cookie(
            key=key,
            value=value,
            max_age=minutes * 60,
            httponly=True,
            samesite="Lax"
        )
    except ValueError:
        flash("Некоректний ключ або значення cookie!", "error")
        return redirect(url_for("users.profile"))

    flash(f"Cookie '{key}' успішно додано!", "success")

    return response


@users_bp.route("/cookies/delete", methods=["POST"])
def delete_cookie():
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "error")
        return redirect(url_for("users.login"))

    key = request.form.get("key", "").strip()

    if not key or key == get_session_cookie_name():
        flash("Некоректний ключ cookie!", "error")
        return redirect(url_for("users.profile"))

    if key not in request.cookies:
        flash(f"Cookie '{key}' не знайдено!", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(key)

    flash(f"Cookie '{key}' успішно видалено!", "success")

    return response


@users_bp.route("/cookies/delete-all", methods=["POST"])
def delete_all_cookies():
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "error")
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))

    keys = [
        key for key in request.cookies
        if key != get_session_cookie_name()
    ]

    for key in keys:
        response.delete_cookie(key)

    if keys:
        flash("Усі користувацькі cookie успішно видалено!", "success")
    else:
        flash("Немає cookie для видалення.", "info")

    return response


@users_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Ви успішно вийшли із системи.", "success")
    return redirect(url_for("users.login"))
