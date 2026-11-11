import json
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from flask import render_template, request, redirect, url_for, flash, current_app

from .forms import ContactForm

log_directory = Path(__file__).resolve().parent.parent / "logs"
log_directory.mkdir(parents=True, exist_ok=True)

contact_logger = logging.getLogger("contact_form")
contact_logger.setLevel(logging.INFO)
contact_logger.propagate = False

if not contact_logger.handlers:
    handler = RotatingFileHandler(
        log_directory / "contact_messages.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )

    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    contact_logger.addHandler(handler)


def register_routes(app):

    @app.route("/")
    def main():
        return render_template("homepage.html", title="Головна")

    @app.route("/homepage")
    def home():
        agent = request.user_agent

        return render_template("homepage.html", title="Головна", agent=agent)

    @app.route("/resume")
    def resume():
        return render_template("resume.html", title="Резюме")

    @app.route("/contacts", methods=["GET", "POST"])
    def contacts():
        form = ContactForm()

        if form.validate_on_submit():
            contact_data = {
                "name": form.name.data,
                "email": form.email.data,
                "phone": form.phone.data,
                "subject": form.subject.data,
                "message": form.message.data,
            }

            try:
                contact_logger.info(json.dumps(contact_data, ensure_ascii=False))
            except (OSError, ValueError):
                current_app.logger.exception(
                    "Не вдалося зберегти контактне повідомлення."
                )

                flash("Помилка збереження повідомлення.", "error")

                return (
                    render_template("contacts.html", title="Контакти", form=form),
                    500,
                )

            flash("Повідомлення успішно надіслано!", "success")

            return redirect(url_for("contacts"))

        if request.method == "POST":
            flash("Форму заповнено некоректно. Перевірте введені дані.", "error")

        return render_template("contacts.html", title="Контакти", form=form)
