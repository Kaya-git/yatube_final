import shutil
import tempfile
from xml.etree.ElementTree import Comment

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Post, Group, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

TEST_TITLE = 'Тестовая группа'
TEST_SLUG = '1234'
TEST_TEXT = 'Тестовый пост'
TEST_USERNAME_AUTHOR = 'author'
TEST_COMMENT = 'Тестовый коментарий'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME_AUTHOR)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=TEST_TEXT,
        )

        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text=TEST_COMMENT,
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.form = PostForm()

        cls.form_data_comment = {
            'text': cls.comment.text,
        }

        cls.form_data_create_post = {
            'group': cls.group.pk,
            'text': cls.post.text,
        }

        cls.form_data_post_edit_form = {
            'text': 'Текст постов',
            'group': cls.group.pk
        }
        cls.form_data_image = {
            'text': 'test_text',
            'image': uploaded,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data_create_post,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text=self.post.text,
            ).exists()
        )

    def test_comment(self):
        """Валидная форма создает запись в Comment"""
        post_id = PostFormTests.post.id
        comments_count = Comment.objects.count()
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=({post_id})),
            data=self.form_data_comment,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args=({post_id})))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=self.comment.text,
            ).exists()
        )

    def test_post_edit_form(self):
        """Валидная форма редактирует запись."""
        post_id = PostFormTests.post.id
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({post_id})),
            data=self.form_data_post_edit_form,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=({post_id}))
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.get(
                id=self.post.id).text, self.form_data_post_edit_form['text']
        )

    def test_create_post_with_image(self):
        """Проверяем, что создается пост с картинкой"""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data_image,
        )
        self.assertTrue(
            Post.objects.filter(
                text='test_text',
                image='posts/small.gif'
            ).exists()
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.user.username])
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
