import logging
from pathlib import Path

from flask import flash, redirect, render_template, request, url_for
from . import app
from .forms import ContactForm

CONTACT_LOG = Path(app.root_path) / "data" / "contacts.log"


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/homepage")
def home():
    agent = request.user_agent.string
    return render_template("homepage.html", agent=agent)


@app.route("/resume")
def resume():
    return render_template("resume.html", name="Орест Качур", profession="Студент та веброзробник")


@app.route("/contact", methods=["GET", "POST"])
@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            CONTACT_LOG.parent.mkdir(parents=True, exist_ok=True)
            logger = logging.getLogger("contact_submissions")
            if not logger.handlers:
                handler = logging.FileHandler(CONTACT_LOG, encoding="utf-8")
                handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
                logger.propagate = False
            logger.info("%s", form.data_for_log())
            flash("Повідомлення успішно записано.", "success")
        except OSError:
            app.logger.exception("Could not write contact submission")
            flash("Не вдалося записати повідомлення. Спробуйте ще раз.", "error")
        return redirect(url_for("contacts"))
    return render_template("contacts.html", form=form)
