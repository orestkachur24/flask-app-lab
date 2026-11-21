from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, ValidationError


CATEGORIES = [("electronics", "Електроніка"), ("home", "Дім"), ("other", "Інше")]


class ProductForm(FlaskForm):
    name = StringField("Назва", validators=[DataRequired(), Length(min=3, max=120)])
    content = TextAreaField("Опис", validators=[DataRequired(), Length(max=5000)])
    price = StringField("Ціна", validators=[DataRequired(), Regexp(r"^\d+(?:[.,]\d{1,2})?$", message="Вкажіть додатну ціну з точністю до двох знаків")])
    category = SelectField("Категорія", choices=CATEGORIES, validators=[DataRequired()])
    quantity = IntegerField("Кількість", validators=[DataRequired(), NumberRange(min=0)])
    image = FileField("Зображення (PNG, JPG, JPEG)")
    submit = SubmitField("Зберегти")

    def validate_price(self, field):
        try:
            if Decimal(field.data.replace(",", ".")) <= 0:
                raise ValidationError("Ціна має бути більшою за нуль.")
        except (ValueError, ArithmeticError):
            raise ValidationError("Вкажіть коректну ціну.")

    def validate_image(self, field):
        upload = field.data
        if upload and getattr(upload, "filename", ""):
            if "." not in upload.filename or upload.filename.rsplit(".", 1)[1].lower() not in {"png", "jpg", "jpeg"}:
                raise ValidationError("Дозволені формати: PNG, JPG, JPEG.")
