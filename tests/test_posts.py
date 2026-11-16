import unittest
from datetime import datetime

from app import create_app, db
from app.posts.models import Post


class PostTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_post(self):
        response = self.client.post(
            "/post/create",
            data={
                "title": "My first post",
                "content": "This is TDD!",
                "category": "tech",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

        post = db.session.scalar(db.select(Post).where(Post.title == "My first post"))

        self.assertIsNotNone(post)
        self.assertEqual(post.content, "This is TDD!")
        self.assertEqual(post.category, "tech")
        self.assertTrue(post.is_active)
        self.assertEqual(post.author, "Anonymous")

    def test_list_posts(self):
        posts = [
            Post(
                title="Перший пост",
                content="Текст першого поста",
                category="news",
                is_active=True,
                posted=datetime(2026, 11, 10, 10, 0),
            ),
            Post(
                title="Другий пост",
                content="Текст другого поста",
                category="tech",
                is_active=True,
                posted=datetime(2026, 11, 12, 12, 0),
            ),
            Post(
                title="Прихований пост",
                content="Цей пост не повинен відображатися",
                category="other",
                is_active=False,
                posted=datetime(2026, 11, 14, 14, 0),
            ),
        ]

        db.session.add_all(posts)
        db.session.commit()

        response = self.client.get("/post")

        self.assertEqual(response.status_code, 200)

        self.assertIn("Перший пост".encode("utf-8"), response.data)

        self.assertIn("Другий пост".encode("utf-8"), response.data)

        self.assertNotIn("Прихований пост".encode("utf-8"), response.data)

        first_position = response.data.find("Перший пост".encode("utf-8"))

        second_position = response.data.find("Другий пост".encode("utf-8"))

        self.assertLess(second_position, first_position)

    def test_view_post_detail(self):
        post = Post(
            title="Детальний перегляд",
            content="Повний текст тестової публікації",
            category="tech",
            is_active=True,
        )

        db.session.add(post)
        db.session.commit()

        response = self.client.get(f"/post/{post.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Детальний перегляд".encode("utf-8"), response.data)
        self.assertIn("Повний текст тестової публікації".encode("utf-8"), response.data)

    def test_update_post(self):
        post = Post(
            title="Старий заголовок",
            content="Старий текст поста",
            category="news",
            is_active=True,
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id
        original_author = post.author

        response = self.client.post(
            f"/post/{post_id}/update",
            data={
                "title": "Оновлений заголовок",
                "content": "Оновлений текст поста",
                "category": "tech",
                "is_active": "y",
                "publish_date": "2026-11-16T16:30",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)

        updated_post = db.session.get(Post, post_id)

        self.assertEqual(updated_post.title, "Оновлений заголовок")
        self.assertEqual(updated_post.content, "Оновлений текст поста")
        self.assertEqual(updated_post.category, "tech")
        self.assertTrue(updated_post.is_active)
        self.assertEqual(original_author, updated_post.author)

    def test_delete_post_confirmation(self):
        post = Post(
            title="Пост для видалення",
            content="Текст поста для видалення",
            category="news",
            is_active=True,
        )

        db.session.add(post)
        db.session.commit()

        response = self.client.get(f"/post/{post.id}/delete")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Пост для видалення".encode("utf-8"), response.data)

        self.assertIsNotNone(db.session.get(Post, post.id))

    def test_delete_post(self):
        post = Post(
            title="Тест видалення",
            content="Пост буде видалений із бази",
            category="tech",
            is_active=True,
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id

        response = self.client.post(f"/post/{post_id}/delete", follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        deleted_post = db.session.get(Post, post_id)

        self.assertIsNone(deleted_post)

    def test_post_not_found(self):
        response = self.client.get("/post/999999")
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/post/999999/update")
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/post/999999/delete")
        self.assertEqual(response.status_code, 404)

    def test_create_post_flash(self):
        response = self.client.post(
            "/post/create",
            data={
                "title": "Flash test",
                "content": "Перевірка повідомлення",
                "category": "news",
                "is_active": "y",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Post added successfully", response.data)

    def test_delete_post_flash(self):
        post = Post(
            title="Пост для перевірки flash",
            content="Тест повідомлення після видалення",
            category="tech",
        )

        db.session.add(post)
        db.session.commit()

        response = self.client.post(f"/post/{post.id}/delete", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Пост успішно видалено!".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
