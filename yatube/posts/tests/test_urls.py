from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


TEST_TITLE = 'Тестовая группа'
TEST_SLUG = 'the_group'
TEST_TEXT = 'Тестовый пост'
TEST_DESCRIPTION = 'Тестовое описание'
TEST_USERNAME_1 = 'test_name_1'
TEST_USERNAME_2 = 'test_name_2'
POST_ID = 1


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.public_urls_templates = {
            '/': 'posts/index.html',
            f'/group/{TEST_SLUG}/': 'posts/group_list.html',
            f'/profile/{TEST_USERNAME_1}/': 'posts/profile.html',
            f'/posts/{POST_ID}/': 'posts/post_detail.html'
        }

        cls.private_urls_templates = {
            '/create/': 'posts/post_create.html',
            f'/posts/{POST_ID}/edit/': 'posts/post_create.html'
        }

        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username=TEST_USERNAME_2),
            text=TEST_TEXT,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user1 = User.objects.create_user(username=TEST_USERNAME_1)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        self.user2 = User.objects.get(username=TEST_USERNAME_2)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user2)

    def test_pages_urls_for_guest_users(self):
        """Проверяем доступность публичных адресов гостевой учеткой"""
        for address in self.public_urls_templates:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_url_redirect_for_guest_users(self):
        """Проверяем редиректы приватных адресов
        гостевой учеткой (корректность редиректа тоже проверяем)"""
        for address in self.private_urls_templates.items():
            with self.subTest(adress=address):
                if address == '/posts/{POST_ID}/edit/':
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response,
                                            reverse('posts:post_detail',
                                                    id({POST_ID}))
                                            )
                if address == '/create/':
                    response = self.guest_client.get(address)
                    self.assertTemplateUsed(response, reverse('users:login'))

    def test_pages_urls_for_authorised_users(self):
        """Проверяем доступность приватных адресов залогиненной учеткой"""
        for address in self.private_urls_templates:
            with self.subTest(address=address):
                if address == '/posts/{POST_ID}/edit/':
                    response = self.authorized_client_author.get(address)
                if address == '/create/':
                    response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_urls_uses_correct_template(self):
        '''Проверяем соответствие шаблонов для публичных адресов'''
        for address, templates in self.public_urls_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, templates)

    def test_private_urls_uses_correct_template(self):
        '''Проверяем соответствие шаблонов для приватных адресов'''
        for address, templates in self.private_urls_templates.items():
            with self.subTest(address=address):
                if address == '/posts/{POST_ID}/edit/':
                    response = self.authorized_client_author.get(address)
                if address == '/create/':
                    response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, templates)

    def test_edit(self):
        """Тест доступности редактирования Автору поста"""
        response = self.authorized_client_author.get(f'/posts/{POST_ID}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_for_auth_users(self):
        """Тест доступности unexisting auth пользователям"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexisting_page_for_guest_users(self):
        """Тест доступности unexisting guest пользователям"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_comments_auth_user(self):
        """Тест доступности коментирования поста авторизованому пользователю"""
        response = self.authorized_client.get(f'/posts/{POST_ID}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_error_page(self):
        """Тест статуса ответа сервера
        и соответствия кастомного шаблона 404.html"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
