from flask import render_template, request
from . import app


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
