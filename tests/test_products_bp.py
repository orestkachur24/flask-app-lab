import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from app import app
from app.products import routes


class FlaskProductsBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "products.json"
        self.upload_path = Path(self.tempdir.name) / "uploads"
        self.db_patch = patch.object(routes, "DB_PATH", self.db_path)
        self.upload_patch = patch.object(routes, "UPLOAD_PATH", self.upload_path)
        self.db_patch.start()
        self.upload_patch.start()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def tearDown(self):
        self.db_patch.stop()
        self.upload_patch.stop()
        self.tempdir.cleanup()

    def test_products_list(self):
        routes.product_table().insert_multiple([
            {"id": 1, "name": "Laptop", "price": "1200.00", "content": "Powerful laptop", "category": "electronics", "quantity": 2, "image": None, "created_at": "now"},
            {"id": 2, "name": "Phone", "price": "800.00", "content": "Smart phone", "category": "electronics", "quantity": 4, "image": None, "created_at": "now"},
            {"id": 3, "name": "PC", "price": "1800.00", "content": "Desktop computer", "category": "electronics", "quantity": 1, "image": None, "created_at": "now"},
        ])
        response = self.client.get("/products/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"Phone", response.data)
        self.assertIn(b"PC", response.data)

    def test_product_detail(self):
        routes.product_table().insert({"id": 2, "name": "Phone", "price": "800.00", "content": "Smart phone", "category": "electronics", "quantity": 4, "image": None, "created_at": "now"})
        response = self.client.get("/products/2")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Phone", response.data)
        self.assertIn(b"800", response.data)

    def test_unknown_product_returns_404(self):
        response = self.client.get("/products/999")

        self.assertEqual(response.status_code, 404)

    def product_data(self):
        return {"name": "Camera", "content": "A good digital camera", "price": "129.99", "category": "electronics", "quantity": "5"}

    def test_create_product_persists_and_redirects(self):
        response = self.client.post("/product/add", data=self.product_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get("/product").status_code, 200)
        product = routes.get_product(1)
        self.assertEqual(product["price"], "129.99")
        self.assertIn("created_at", product)

    def test_edit_product_preserves_identity_and_created_time(self):
        response = self.client.post("/product/add", data=self.product_data())
        self.assertEqual(response.status_code, 302)
        created_at = routes.get_product(1)["created_at"]
        data = self.product_data()
        data["name"] = "Camera Pro"
        data["price"] = "239.50"
        response = self.client.post("/product/1/edit", data=data)
        self.assertEqual(response.status_code, 302)
        updated = routes.get_product(1)
        self.assertEqual(updated["name"], "Camera Pro")
        self.assertEqual(updated["id"], 1)
        self.assertEqual(updated["created_at"], created_at)

    def test_delete_product(self):
        self.client.post("/product/add", data=self.product_data())
        response = self.client.post("/product/1/delete")
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(routes.get_product(1))


if __name__ == "__main__":
    unittest.main()
