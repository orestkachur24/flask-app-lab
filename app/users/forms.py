from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

from .models import User
from .. import db


class RegistrationForm(FlaskForm):
    username = StringField(
        "Ім’я користувача",
        validators=[DataRequired(), Length(min=3, max=20), Regexp(r"^[A-Za-z0-9._]+$", message="Використовуйте лише літери, цифри, крапку та _.")],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Підтвердження пароля", validators=[DataRequired(), EqualTo("password", message="Паролі мають збігатися.")]
    )
    submit = SubmitField("Зареєструватися")

    def validate_username(self, field):
        existing = db.session.execute(db.select(User).where(User.username == field.data)).scalar_one_or_none()
        if existing:
            raise ValidationError("Це ім’я користувача вже зайняте.")

    def validate_email(self, field):
        existing = db.session.execute(db.select(User).where(User.email == field.data.lower())).scalar_one_or_none()
        if existing:
            raise ValidationError("Користувач із такою електронною адресою вже існує.")


class LoginForm(FlaskForm):
    username = StringField("Ім’я користувача або email", validators=[DataRequired(), Length(max=255)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Увійти")
