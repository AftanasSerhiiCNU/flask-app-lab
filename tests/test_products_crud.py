import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app import create_app

app = create_app("testing")

from app.products.database import (
    get_products,
    get_product,
    create_product,
    update_product,
    delete_product,
)


class ProductCRUDTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_config = {
            "TESTING": app.config["TESTING"],
            "WTF_CSRF_ENABLED": app.config.get("WTF_CSRF_ENABLED", True),
            "PRODUCTS_DB_PATH": app.config.get("PRODUCTS_DB_PATH"),
        }

        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB_PATH=str(Path(self.temp_dir.name) / "products.json"),
        )

        self.app_context = app.app_context()
        self.app_context.push()

        self.client = app.test_client()

        self.product_data = {
            "name": "Тестовий ноутбук",
            "content": "Ноутбук для тестування CRUD",
            "price": Decimal("15000.50"),
            "category": "electronics",
            "quantity": 5,
            "image": None,
        }

        self.form_data = {
            "name": "Тестовий ноутбук",
            "content": "Ноутбук для тестування CRUD",
            "price": "15000.50",
            "category": "electronics",
            "quantity": "5",
        }

    def tearDown(self):
        self.app_context.pop()

        for key, value in self.original_config.items():
            if key == "PRODUCTS_DB_PATH" and value is None:
                app.config.pop(key, None)
            else:
                app.config[key] = value

        self.temp_dir.cleanup()

    def test_create_product(self):
        product_id = create_product(self.product_data)

        product = get_product(product_id)

        self.assertIsNotNone(product)
        self.assertEqual(product["name"], "Тестовий ноутбук")
        self.assertEqual(product["price"], "15000.50")
        self.assertEqual(product["quantity"], 5)
        self.assertIn("created_at", product)

    def test_get_products(self):
        create_product(self.product_data)
        create_product({**self.product_data, "name": "Другий ноутбук"})

        products = get_products()

        self.assertEqual(len(products), 2)

    def test_get_product_by_id(self):
        product_id = create_product(self.product_data)

        product = get_product(product_id)

        self.assertEqual(product["id"], product_id)
        self.assertEqual(product["category"], "electronics")

    def test_update_product(self):
        product_id = create_product(self.product_data)

        original = get_product(product_id)

        result = update_product(
            product_id,
            {"name": "Оновлений ноутбук", "price": "12000.99", "quantity": 10},
        )

        updated = get_product(product_id)

        self.assertTrue(result)
        self.assertEqual(updated["name"], "Оновлений ноутбук")
        self.assertEqual(updated["price"], "12000.99")
        self.assertEqual(updated["quantity"], 10)
        self.assertEqual(updated["created_at"], original["created_at"])
        self.assertEqual(updated["id"], original["id"])

    def test_delete_product(self):
        product_id = create_product(self.product_data)

        result = delete_product(product_id)

        self.assertTrue(result)
        self.assertIsNone(get_product(product_id))

    def test_nonexistent_product(self):
        self.assertIsNone(get_product(99999))
        self.assertFalse(update_product(99999, {"name": "Test"}))
        self.assertFalse(delete_product(99999))

    def test_product_list_page(self):
        create_product(self.product_data)

        response = self.client.get("/product")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Тестовий ноутбук".encode("utf-8"), response.data)

    def test_product_detail_page(self):
        product_id = create_product(self.product_data)

        response = self.client.get(f"/product/{product_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Тестовий ноутбук".encode("utf-8"), response.data)

    def test_product_not_found_page(self):
        response = self.client.get("/product/99999")

        self.assertEqual(response.status_code, 404)

    def test_create_product_via_post(self):
        response = self.client.post(
            "/product/add", data=self.form_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        products = get_products()

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["name"], "Тестовий ноутбук")

    def test_invalid_product_name(self):
        invalid_data = {**self.form_data, "name": "AB"}

        response = self.client.post("/product/add", data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(get_products()), 0)

        self.assertIn("Назва повинна містити".encode("utf-8"), response.data)

    def test_invalid_product_quantity(self):
        invalid_data = {**self.form_data, "quantity": "-5"}

        response = self.client.post("/product/add", data=invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(get_products()), 0)

    def test_edit_product_via_post(self):
        product_id = create_product(self.product_data)
        original = get_product(product_id)

        updated_data = {
            **self.form_data,
            "name": "Оновлений ноутбук",
            "price": "9999.99",
            "quantity": "12",
        }

        response = self.client.post(
            f"/product/{product_id}/edit", data=updated_data, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        updated = get_product(product_id)

        self.assertEqual(updated["name"], "Оновлений ноутбук")
        self.assertEqual(updated["price"], "9999.99")
        self.assertEqual(updated["quantity"], 12)
        self.assertEqual(updated["created_at"], original["created_at"])

    def test_delete_product_via_post(self):
        product_id = create_product(self.product_data)

        response = self.client.post(
            f"/product/{product_id}/delete", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(get_product(product_id))

    def test_data_persistence(self):
        product_id = create_product(self.product_data)

        database_file = Path(app.config["PRODUCTS_DB_PATH"])

        self.assertTrue(database_file.exists())

        product = get_product(product_id)

        self.assertEqual(product["name"], "Тестовий ноутбук")


if __name__ == "__main__":
    unittest.main()
