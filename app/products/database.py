from datetime import datetime, timezone
from pathlib import Path

from flask import current_app
from tinydb import TinyDB


def get_database():
    database_path = current_app.config.get("PRODUCTS_DB_PATH")

    if not database_path:
        database_path = Path(current_app.root_path).parent / "data" / "products.json"

    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    return TinyDB(database_path)


def get_products():
    with get_database() as db:
        table = db.table("products")

        products = []

        for document in table.all():
            product = dict(document)
            product["id"] = document.doc_id
            products.append(product)

        return products


def get_product(product_id):
    with get_database() as db:
        table = db.table("products")
        document = table.get(doc_id=product_id)

        if document is None:
            return None

        product = dict(document)
        product["id"] = document.doc_id

        return product


def create_product(data):
    product = {
        "name": data["name"],
        "content": data["content"],
        "price": str(data["price"]),
        "category": data["category"],
        "quantity": data["quantity"],
        "image": data.get("image"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with get_database() as db:
        table = db.table("products")
        product_id = table.insert(product)

    return product_id


def update_product(product_id, data):
    with get_database() as db:
        table = db.table("products")

        if not table.contains(doc_id=product_id):
            return False

        table.update(data, doc_ids=[product_id])

        return True


def delete_product(product_id):
    with get_database() as db:
        table = db.table("products")

        if not table.contains(doc_id=product_id):
            return False

        table.remove(doc_ids=[product_id])

        return True
