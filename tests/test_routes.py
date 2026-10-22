import unittest
from app import app


class FlaskRoutesTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_resume(self):
        response = self.client.get("/resume")
        self.assertEqual(response.status_code, 200)

    def test_contacts(self):
        response = self.client.get("/contacts")
        self.assertEqual(response.status_code, 200)

    def test_users_greetings(self):
        response = self.client.get("/users/hi/John?age=30")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"JOHN", response.data)

    def test_users_admin_redirect(self):
        response = self.client.get("/users/admin")
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/users/hi/administrator?age=45",
            response.headers["Location"]
        )

    def test_products_list(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)

    def test_product_detail(self):
        response = self.client.get("/products/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)

    def test_product_not_found(self):
        response = self.client.get("/products/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
