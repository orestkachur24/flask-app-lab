import unittest

from app import create_app, db
from app.posts.models import Post
from app.posts.tags import Tag
from app.users.models import User


class PostsCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            user = User(username="tester", email="tester@example.com", password="test-hash")
            tag = Tag(name="test-tag")
            db.session.add_all([user, tag])
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @staticmethod
    def post_data(title="Мій перший пост", content="Це достатньо довгий текст для нового поста."):
        return {"title": title, "content": content, "enabled": "y", "category": "news",
                "publish_date": "2026-11-21T12:30", "author_id": "1", "tags": ["1"]}

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
            self.assertEqual(post.user.username, "tester")
            self.assertEqual(post.category.value, "news")
            self.assertEqual([tag.name for tag in post.tags], ["test-tag"])

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

    def test_post_author_and_tags_relationships(self):
        self.create_post()
        with self.app.app_context():
            user = db.session.get(User, 1)
            tag = db.session.get(Tag, 1)
            self.assertEqual([post.title for post in user.posts], ["Мій перший пост"])
            self.assertEqual([post.title for post in tag.posts], ["Мій перший пост"])

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
