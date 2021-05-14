import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='JohnDoe')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='slug-for-test',
            description='Тестовое описание'
        )
        cls.group_2 = Group.objects.create(
            title='TestTitle2',
            slug='slug-for-test-2',
            description='Тестовое описание 2'
        )
        cls.post = Post.objects.create(
            text='firsttext',
            author=cls.user,
            group=cls.group,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        created_post = self.authorized_client.get(
            reverse('post',
                    kwargs={
                        'username': 'JohnDoe',
                        'post_id': 1,
                    }
                    )
        )
        context_post = created_post.context['post']
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(context_post.author, self.user)
        self.assertEqual(context_post.group, self.group)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Текст из формы',
            author=self.user,
            group=self.group,
            image='posts/small.gif').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_user_cant_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Try to create post',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertFalse(Post.objects.filter(
            text='Try to create post',
            group=self.group).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'secondtext',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': 'JohnDoe',
                'post_id': 1}),
            data=form_data, )
        edited_post = self.authorized_client.get(
            reverse('post',
                    kwargs={
                        'username': 'JohnDoe',
                        'post_id': 1}))
        context_post = edited_post.context['post']
        self.assertEqual(context_post.author, self.user)
        self.assertEqual(context_post.group, self.group_2)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(Post.objects.filter(
            text='secondtext',
            group=self.group_2).exists())
        self.assertFalse(Post.objects.filter(
            text='secondtext',
            group=self.group).exists())
        self.assertRedirects(response, '/JohnDoe/1/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
