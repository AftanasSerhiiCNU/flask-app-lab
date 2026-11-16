from datetime import datetime, timezone

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    DateTimeLocalField,
    SelectField,
    SelectChoice,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, Optional

CATEGORIES = [
    SelectChoice("news", "Новини"),
    SelectChoice("publication", "Публікації"),
    SelectChoice("tech", "Технології"),
    SelectChoice("other", "Інше"),
]


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[
            DataRequired(message="Введіть заголовок."),
            Length(
                min=2,
                max=150,
                message="Заголовок повинен містити від 2 до 150 символів.",
            ),
        ],
    )

    content = TextAreaField(
        "Текст публікації",
        validators=[DataRequired(message="Введіть текст публікації.")],
        render_kw={"rows": 5, "cols": 40},
    )

    is_active = BooleanField("Активний пост", default=True)

    publish_date = DateTimeLocalField(
        "Дата публікації",
        format="%Y-%m-%dT%H:%M",
        default=lambda: datetime.now(timezone.utc).replace(
            tzinfo=None, second=0, microsecond=0
        ),
        validators=[Optional()],
    )

    category = SelectField(
        "Категорія",
        choices=CATEGORIES,
        validators=[DataRequired(message="Оберіть категорію.")],
    )

    submit = SubmitField("Зберегти пост")

class DeletePostForm(FlaskForm):
    submit = SubmitField("Так, видалити")
