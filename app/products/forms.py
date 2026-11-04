from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileSize
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    SelectChoice,
    IntegerField,
    FileField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    ValidationError,
)

PRODUCT_CATEGORIES = {
    "electronics": "Електроніка",
    "clothing": "Одяг",
    "books": "Книги",
    "home": "Для дому",
    "other": "Інше",
}


class ProductForm(FlaskForm):
    name = StringField(
        "Назва товару",
        validators=[
            DataRequired(message="Введіть назву товару."),
            Length(
                min=3, max=100, message="Назва повинна містити від 3 до 100 символів."
            ),
        ],
    )

    content = TextAreaField(
        "Опис товару",
        validators=[DataRequired(message="Введіть опис товару.")],
        render_kw={"rows": 5, "cols": 40},
    )

    price = DecimalField(
        "Ціна (грн)",
        places=2,
        validators=[
            InputRequired(message="Введіть ціну товару."),
            NumberRange(min=Decimal("0.01"), message="Ціна повинна бути більшою за 0."),
        ],
    )

    category = SelectField(
        "Категорія",
        choices=[
            SelectChoice("", "Оберіть категорію"),
            *[
                SelectChoice(value, label)
                for value, label in PRODUCT_CATEGORIES.items()
            ],
        ],
        validators=[DataRequired(message="Оберіть категорію товару.")],
    )

    quantity = IntegerField(
        "Кількість",
        validators=[
            InputRequired(message="Введіть кількість товару."),
            NumberRange(min=0, message="Кількість не може бути від'ємною."),
        ],
    )

    image = FileField(
        "Зображення товару",
        validators=[
            FileAllowed(
                ["png", "jpg", "jpeg"], message="Дозволені лише PNG, JPG і JPEG."
            ),
            FileSize(
                max_size=2 * 1024 * 1024,
                message="Розмір зображення не повинен перевищувати 2 МБ.",
            ),
        ],
    )

    submit = SubmitField("Зберегти товар")

    def validate_price(self, field):
        if field.data is None:
            return

        if field.data != field.data.quantize(Decimal("0.01")):
            raise ValidationError(
                "Ціна повинна містити не більше двох знаків після коми."
            )
