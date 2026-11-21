from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeLocalField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PostForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(min=3, max=150)])
    content = TextAreaField("Текст поста", validators=[DataRequired(), Length(min=10, max=20000)])
    enabled = BooleanField("Опублікований", default=True)
    publish_date = DateTimeLocalField("Дата і час публікації", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    category = SelectField("Категорія", choices=[("news", "Новина"), ("publication", "Публікація"), ("tech", "Технології"), ("other", "Інше")], validators=[DataRequired()])
    author_id = SelectField("Автор", coerce=int, validators=[DataRequired()])
    tags = SelectMultipleField("Теги", coerce=int)
    submit = SubmitField("Зберегти")
