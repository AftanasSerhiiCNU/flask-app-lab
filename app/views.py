
from flask import render_template, request
from . import app


@app.route("/")
def main():
    return render_template("homepage.html", title="Головна")


@app.route("/homepage")
def home():
    agent = request.user_agent
    return render_template(
        "homepage.html",
        title="Головна",
        agent=agent
    )


@app.route("/resume")
def resume():
    return render_template("resume.html", title="Резюме")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html", title="Контакти")
