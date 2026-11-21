import re

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TelField, TextAreaField
from wtforms.validators import Email, Length, Regexp, DataRequired


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=4, max=10)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = TelField("Phone", validators=[DataRequired(), Regexp(r"^\+380\d{9}$", message="Формат телефону: +380XXXXXXXXX")])
    subject = SelectField("Subject", choices=[("general", "Загальне питання"), ("support", "Підтримка"), ("feedback", "Відгук")], validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Send Message")

    def data_for_log(self):
        return {"name": self.name.data, "email": self.email.data, "phone": self.phone.data,
                "subject": self.subject.data, "message": self.message.data}
