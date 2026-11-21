import unittest

from app import create_app, db
from app.users.models import User


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def register(self, username="test_user", email="test@example.com", password="StrongPass123"):
        return self.client.post("/users/register", data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
            "submit": "Зареєструватися",
        }, follow_redirects=True)

    def login(self, username="test_user", password="StrongPass123"):
        return self.client.post("/users/login", data={
            "username": username, "password": password, "submit": "Увійти",
        }, follow_redirects=True)

    def test_register_and_store_bcrypt_hash(self):
        response = self.register()
        user = db.session.scalar(db.select(User).where(User.username == "test_user"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Особистий кабінет".encode(), response.data)
        self.assertIsNotNone(user)
        self.assertTrue(user.password.startswith(("$2a$", "$2b$", "$2y$")))
        self.assertTrue(user.check_password("StrongPass123"))

    def test_registration_rejects_duplicate_email(self):
        self.register()
        self.client.post("/users/logout", follow_redirects=True)
        response = self.register(username="second_user")
        self.assertIn("такою електронною адресою".encode(), response.data)
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(User)), 1)

    def test_login_success_and_failure(self):
        self.register()
        self.client.post("/users/logout")
        success = self.login()
        self.assertIn(b"test_user", success.data)
        self.client.post("/users/logout")
        failure = self.login(password="wrong-password")
        self.assertIn("Неправильне ім’я".encode(), failure.data)

    def test_account_and_user_list_require_login(self):
        response = self.client.get("/users/account")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login", response.location)
        self.register()
        account = self.client.get("/users/account")
        users = self.client.get("/users/all")
        self.assertEqual(account.status_code, 200)
        self.assertIn(b"test@example.com", account.data)
        self.assertEqual(users.status_code, 200)
        self.assertIn(b"1", users.data)

    def test_logout_clears_authentication(self):
        self.register()
        response = self.client.post("/users/logout", follow_redirects=True)
        self.assertIn("успішно вийшли".encode(), response.data)
        self.assertEqual(self.client.get("/users/account").status_code, 302)

    def test_auth_pages_load(self):
        self.assertEqual(self.client.get("/users/register").status_code, 200)
        self.assertEqual(self.client.get("/users/login").status_code, 200)


if __name__ == "__main__":
    unittest.main()
