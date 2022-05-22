import tempfile

from django import forms
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from ..models import Group, Post, User, Follow


TEST_TITLE = 'Group-title'
TEST_SLUG = 'group-slug'
TEST_TITLE_2 = 'Group-title2'
TEST_SLUG_2 = 'group-slug2'
TEST_TEXT = 'Тестовый пост'
TEST_DESCRIPTION = 'Тестовое описание'
TEST_USERNAME_AUTHOR = 'author'
TEST_USERNAME_AUTHOR_2 = 'author2'
TEST_USERNAME_USER = 'HasNoName'
POST_ID = 10
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        POSTS_AMOUNT = 13

        cls.author = User.objects.create(username=TEST_USERNAME_AUTHOR)

        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

        cls.posts = [
            Post(text=f'Test text {i+1}', author=cls.author, image=cls.image)
            for i in range(POSTS_AMOUNT)
        ]

        Post.objects.bulk_create(cls.posts)

        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
        )

        cls.group2 = Group.objects.create(
            title=TEST_TITLE_2,
            slug=TEST_SLUG_2,
        )

        cls.templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': POST_ID}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': POST_ID}
            ): 'posts/post_create.html',
        }

        cls.form_fields_create_post_context = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        cls.form_fields_post_context = {
            'text': forms.fields.CharField,
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=TEST_USERNAME_USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_id = first_object.id
        self.assertEqual(post_text, f'Test text {post_id}')

    def test_first_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_posts_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['group']
        group_title = first_object.title
        group_slug = first_object.slug
        self.assertEqual(group_title, self.group.title)
        self.assertEqual(group_slug, self.group.slug)

    def test_first_group_page(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_second_group_page(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.author})
        )
        first_object = response.context['page_obj'][1]
        posts = first_object.text
        post_id = first_object.id
        self.assertEqual(posts, f'Test text {post_id}')
        self.assertEqual(response.context['author'].username, 'author')

    def test_first_profile_page(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.author})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.author}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': POST_ID})
        )
        first_object = response.context['post']
        posts = first_object.text
        self.assertEqual(posts, 'Test text 10')

    def test_create_post_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields_create_post_context.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_update_post_context(self):
        """Шаблон update_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': POST_ID})
        )
        for value, expected in self.form_fields_post_context.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def index_test_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        posts_amount = len(response.context['page_obj'])
        post = Post.objects.filter(id=1)
        post.delete()
        posts_amount_deleted = len(response.context['page_obj'])
        self.assertEqual(posts_amount, posts_amount_deleted)
        cache.clear()
        posts_amount_clear = len(response.context['page_obj'])
        self.assertEqual(posts_amount, posts_amount_clear)

    def autorized_client_follow_unfollow_author(self):
        Follow.objects.get_or_create(
            author=TEST_USERNAME_AUTHOR_2,
            user=self.user,
        )
        response_follow = self.authorized_client.get(
            reverse('post:profile_follow',
                    kwargs={'username': TEST_USERNAME_AUTHOR}))
        follows_amount = len(response_follow.follow)
        self.assertEqual(follows_amount, 2)
        response_unfollow = self.authorized_client.get(
            reverse('post:profile_unfollow',
                    kwargs={'username': TEST_USERNAME_AUTHOR_2})
        )
        unfollows_amount = len(response_unfollow.follow)
        self.assertEqual(unfollows_amount, 1)
