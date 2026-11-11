import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image
from werkzeug.datastructures import FileStorage

from app import create_app

app = create_app("testing")

from app.products.database import get_products, get_product
from app.products.images import save_product_image


class ProductImagesTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_config = {
            key: app.config.get(key)
            for key in (
                "TESTING",
                "WTF_CSRF_ENABLED",
                "PRODUCTS_DB_PATH",
                "PRODUCTS_UPLOAD_DIR",
            )
        }

        self.original_keys = set(app.config)

        self.upload_directory = Path(self.temp_dir.name) / "uploads"

        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB_PATH=str(Path(self.temp_dir.name) / "products.json"),
            PRODUCTS_UPLOAD_DIR=str(self.upload_directory),
        )

        self.context = app.app_context()
        self.context.push()

        self.client = app.test_client()

    def tearDown(self):
        self.context.pop()

        for key, value in self.original_config.items():
            if key in self.original_keys:
                app.config[key] = value
            else:
                app.config.pop(key, None)

        self.temp_dir.cleanup()

    def make_image(self, image_format="PNG"):
        stream = BytesIO()

        image = Image.new("RGB", (100, 100), color="blue")

        image.save(stream, format=image_format)
        stream.seek(0)

        return stream

    def make_file(self, filename, image_format="PNG"):
        return FileStorage(
            stream=self.make_image(image_format),
            filename=filename,
            content_type="image/png",
        )

    def get_form_data(self, image=None):
        data = {
            "name": "Тестовий товар",
            "content": "Опис тестового товару",
            "price": "1500.50",
            "category": "electronics",
            "quantity": "5",
        }

        if image is not None:
            data["image"] = image

        return data

    def test_save_png_image(self):
        file = self.make_file("product.png")

        path = save_product_image(file)

        self.assertTrue(path.startswith("uploads/"))
        self.assertTrue(path.endswith(".png"))
        self.assertTrue((self.upload_directory / Path(path).name).exists())

    def test_save_jpg_image(self):
        file = self.make_file("product.jpg", "JPEG")

        path = save_product_image(file)

        self.assertTrue(path.endswith(".jpg"))
        self.assertTrue((self.upload_directory / Path(path).name).exists())

    def test_save_jpeg_image(self):
        file = self.make_file("product.jpeg", "JPEG")

        path = save_product_image(file)

        self.assertTrue(path.endswith(".jpeg"))

    def test_unique_filenames(self):
        first = save_product_image(self.make_file("product.png"))

        second = save_product_image(self.make_file("product.png"))

        self.assertNotEqual(first, second)

    def test_invalid_extension(self):
        file = FileStorage(stream=BytesIO(b"Test document"), filename="document.txt")

        with self.assertRaises(ValueError):
            save_product_image(file)

    def test_fake_image(self):
        file = FileStorage(stream=BytesIO(b"This is not an image"), filename="fake.jpg")

        with self.assertRaises(ValueError):
            save_product_image(file)

    def test_mismatched_image_format(self):
        file = self.make_file("fake.jpg", "PNG")

        with self.assertRaises(ValueError):
            save_product_image(file)

    def test_oversized_image(self):
        file = FileStorage(
            stream=BytesIO(b"a" * (2 * 1024 * 1024 + 1)), filename="large.png"
        )

        with self.assertRaises(ValueError):
            save_product_image(file)

    def test_create_product_with_image(self):
        response = self.client.post(
            "/product/add",
            data=self.get_form_data((self.make_image(), "product.png")),
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

        products = get_products()

        self.assertEqual(len(products), 1)
        self.assertIsNotNone(products[0]["image"])

        image_path = self.upload_directory / Path(products[0]["image"]).name

        self.assertTrue(image_path.exists())

    def test_create_product_without_image(self):
        response = self.client.post(
            "/product/add", data=self.get_form_data(), follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        products = get_products()

        self.assertEqual(len(products), 1)
        self.assertIsNone(products[0]["image"])

    def test_reject_fake_image_via_post(self):
        data = self.get_form_data((BytesIO(b"Invalid image"), "fake.jpg"))

        response = self.client.post(
            "/product/add", data=data, content_type="multipart/form-data"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(get_products()), 0)

    def test_keep_previous_image_on_edit(self):
        response = self.client.post(
            "/product/add",
            data=self.get_form_data((self.make_image(), "product.png")),
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 302)

        product = get_products()[0]
        original_image = product["image"]

        response = self.client.post(
            f"/product/{product['id']}/edit",
            data={**self.get_form_data(), "price": "2000.00"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

        updated = get_product(product["id"])

        self.assertEqual(updated["image"], original_image)
        self.assertEqual(updated["price"], "2000.00")


if __name__ == "__main__":
    unittest.main()
