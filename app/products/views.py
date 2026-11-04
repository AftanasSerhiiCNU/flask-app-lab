from flask_wtf import FlaskForm
from flask import render_template, redirect, url_for, flash, abort, request
from decimal import Decimal
from . import products_bp
from .forms import ProductForm, PRODUCT_CATEGORIES
from .database import (
    get_products,
    get_product,
    create_product,
    update_product,
    delete_product,
)
from .images import save_product_image


@products_bp.route("")
@products_bp.route("/")
def product_list():
    products = get_products()

    return render_template(
        "products/products.html",
        title="Список товарів",
        products=products,
        categories=PRODUCT_CATEGORIES,
    )


@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    delete_form = FlaskForm()

    return render_template(
        "products/detail_product.html",
        title=product["name"],
        product=product,
        categories=PRODUCT_CATEGORIES,
        delete_form=delete_form,
    )


@products_bp.route("/add", methods=["GET", "POST"])
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        try:
            image_path = save_product_image(form.image.data)
        except (ValueError, OSError):
            flash("Не вдалося зберегти зображення товару.", "error")
            return render_template("products/add.html", title="Додати товар", form=form)

        product_data = {
            "name": form.name.data,
            "content": form.content.data,
            "price": form.price.data,
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image_path,
        }

        product_id = create_product(product_data)

        flash("Товар успішно додано!", "success")

        return redirect(url_for("products.product_detail", product_id=product_id))

    if request.method == "POST":
        flash("Перевірте правильність введених даних.", "error")

    return render_template("products/add.html", title="Додати товар", form=form)


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    form = ProductForm()

    if request.method == "GET":
        form.name.data = product["name"]
        form.content.data = product["content"]
        form.price.data = Decimal(product["price"])
        form.category.data = product["category"]
        form.quantity.data = product["quantity"]

    if form.validate_on_submit():
        image_path = product.get("image")

        if form.image.data and form.image.data.filename:
            try:
                image_path = save_product_image(form.image.data)
            except (ValueError, OSError):
                flash("Не вдалося зберегти зображення.", "error")
                return render_template(
                    "products/edit.html",
                    title="Редагувати товар",
                    form=form,
                    product=product,
                )

        product_data = {
            "name": form.name.data,
            "content": form.content.data,
            "price": str(form.price.data),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image_path,
        }

        update_product(product_id, product_data)

        flash("Товар успішно оновлено!", "success")

        return redirect(url_for("products.product_detail", product_id=product_id))

    if request.method == "POST":
        flash("Перевірте правильність введених даних.", "error")

    return render_template(
        "products/edit.html", title="Редагувати товар", form=form, product=product
    )


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
def remove_product(product_id):
    form = FlaskForm()

    if not form.validate_on_submit():
        abort(400)

    product = get_product(product_id)

    if product is None:
        abort(404)

    delete_product(product_id)

    flash("Товар успішно видалено!", "success")

    return redirect(url_for("products.product_list"))
