
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Резюме",
        name="Орест Качур",
        profession="Python Developer"
    )


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    message = None

    if request.method == "POST":
        message = "Дякуємо! Це демонстраційна форма. Повідомлення не надсилалося."

    return render_template(
        "contacts.html",
        title="Контакти",
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)
