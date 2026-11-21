import unittest

from app import create_app, db
from app.posts.models import Post


class PostsCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @staticmethod
    def post_data(title="Мій перший пост", content="Це достатньо довгий текст для нового поста."):
        return {"title": title, "content": content, "enabled": "y", "category": "news", "publish_date": "2026-11-21T12:30"}

    def create_post(self):
        response = self.client.post("/post/create", data=self.post_data())
        self.assertEqual(response.status_code, 302)
        return 1

    def test_create_post(self):
        response = self.client.post("/post/create", data=self.post_data())
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            post = db.session.get(Post, 1)
            self.assertEqual(post.title, "Мій перший пост")
            self.assertEqual(post.author, "Anonymous")
            self.assertEqual(post.category.value, "news")

    def test_logged_in_user_becomes_author(self):
        with self.client.session_transaction() as user_session:
            user_session["username"] = "Orest"
        self.create_post()
        with self.app.app_context():
            self.assertEqual(db.session.get(Post, 1).author, "Orest")

    def test_invalid_post_is_not_saved(self):
        response = self.client.post("/post/create", data=self.post_data("Hi", "Tiny"))
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Post)), 0)

    def test_list_posts(self):
        self.create_post()
        response = self.client.get("/post")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Мій перший пост".encode(), response.data)

    def test_inactive_posts_are_not_listed(self):
        self.create_post()
        data = self.post_data("Чернетка поста", "Цей неактивний текст не повинен з'явитись у списку.")
        data.pop("enabled")
        self.client.post("/post/create", data=data)
        response = self.client.get("/post")
        self.assertIn("Мій перший пост".encode(), response.data)
        self.assertNotIn("Чернетка поста".encode(), response.data)

    def test_view_post_detail(self):
        self.create_post()
        response = self.client.get("/post/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("достатньо довгий текст".encode(), response.data)

    def test_update_post(self):
        self.create_post()
        response = self.client.post("/post/1/update", data=self.post_data("Оновлений заголовок", "Оновлений текст достатньої довжини."))
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            self.assertEqual(db.session.get(Post, 1).title, "Оновлений заголовок")

    def test_delete_post(self):
        self.create_post()
        confirmation = self.client.get("/post/1/delete")
        self.assertEqual(confirmation.status_code, 200)
        self.assertIn("Мій перший пост".encode(), confirmation.data)
        response = self.client.post("/post/1/delete")
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Post, 1))

    def test_404_not_found(self):
        response = self.client.get("/post/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)


if __name__ == "__main__":
    unittest.main()
