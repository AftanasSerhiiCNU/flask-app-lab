from flask import render_template, abort
from . import products_bp


products = [
    {
        "id": 1,
        "name": "Laptop",
        "description": "Ноутбук для роботи та навчання",
        "price": 25000
    },
    {
        "id": 2,
        "name": "Phone",
        "description": "Смартфон із сучасними функціями",
        "price": 15000
    },
    {
        "id": 3,
        "name": "PC",
        "description": "Персональний комп'ютер для роботи та ігор",
        "price": 35000
    }
]


@products_bp.route("/")
def product_list():
    return render_template(
        "products/products.html",
        title="Список товарів",
        products=products
    )


@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = next(
        (p for p in products if p["id"] == product_id),
        None
    )

    if product is None:
        abort(404)

    return render_template(
        "products/detail_product.html",
        title=product["name"],
        product=product
    )
