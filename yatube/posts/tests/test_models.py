from django.test import TestCase

from ..models import Group, Post, User


TEST_TITLE = 'Тестовая группа'
TEST_SLUG = 'Тестовый слаг'
TEST_TEXT = 'Новый пост для тестирования'
TEST_DESCRIPTION = 'Тестовое описание'
TEST_USERNAME_USER = 'auth'


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME_USER)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostsModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

        post = PostsModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
