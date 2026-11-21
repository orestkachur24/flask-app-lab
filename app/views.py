import logging
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from .forms import ContactForm

site_bp = Blueprint("site", __name__)
CONTACT_LOG = Path(__file__).resolve().parent / "data" / "contacts.log"


@site_bp.route("/")
def main():
    return render_template("index.html")


@site_bp.route("/homepage")
def home():
    agent = request.user_agent.string
    return render_template("homepage.html", agent=agent)


@site_bp.route("/resume")
def resume():
    return render_template("resume.html", name="Орест Качур", profession="Студент та веброзробник")


@site_bp.route("/contact", methods=["GET", "POST"])
@site_bp.route("/contacts", methods=["GET", "POST"])
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
            logging.exception("Could not write contact submission")
            flash("Не вдалося записати повідомлення. Спробуйте ще раз.", "error")
        return redirect(url_for("site.contacts"))
    return render_template("contacts.html", form=form)
