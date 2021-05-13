import shutil
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Follow

User = get_user_model()


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.list_dir = os.listdir(os.getcwd())
        cls.author = User.objects.create_user(username='TestUser')
        cls.another_user = User.objects.create_user(username='AnotherUser')
        cls.third_user = User.objects.create_user(username='ThirdUser')
        cls.subscription = Follow.objects.create(user=cls.another_user,
                                                 author=cls.author)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug')
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
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded
        )
        cls.templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': 'test-slug'})
            ),
        }
        cls.form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField,
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        for path in os.listdir(os.getcwd()):
            if path not in cls.list_dir:
                shutil.rmtree(path, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.another_authorized = Client()
        self.third_authorized = Client()
        self.authorized_client.force_login(self.author)
        self.another_authorized.force_login(self.another_user)
        self.third_authorized.force_login(self.third_user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def templates_for_asserts(self, prepared_post):
        """Подготавливаем однотипные тесты"""
        post_text = prepared_post.text
        post_pub_date = prepared_post.pub_date
        post_author = prepared_post.author
        post_group = prepared_post.group
        post_image = prepared_post.image
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(post_author, self.author)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_image, self.post.image)

    def test_index_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_post = response.context['page'][0]
        self.templates_for_asserts(first_post)

    def test_group_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        group_post = response.context['group']
        page_post = response.context['page'][0]
        group_title = group_post.title
        group_description = group_post.description
        group_slug = group_post.slug
        page_image = page_post.image
        self.assertEqual(group_title, self.group.title)
        self.assertEqual(group_description, self.group.description)
        self.assertEqual(group_slug, self.group.slug)
        self.assertEqual(page_image, self.post.image)
        self.assertIn(self.post, response.context['page'])

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get('/TestUser/')
        page_post = response.context['page'][0]
        profile_post = response.context['profile']
        self.templates_for_asserts(page_post)
        self.assertEqual(profile_post, self.author)

    def test_post_view_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом"""
        response = self.authorized_client.get('/TestUser/1/')
        post_context = response.context['post']
        profile_context = response.context['profile']
        self.assertEqual(post_context, self.post)
        self.assertEqual(profile_context, self.author)

    def test_edit_shows_correct_context(self):
        """Шаблон new для редактирования сформирован с правильным контекстом"""
        response = self.authorized_client.get('/TestUser/1/edit/')
        post_context = response.context['post']
        self.assertEqual(post_context, self.post)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_post_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_follow_index_shows_correct_context(self):
        """Шаблон follow сформирован с правильным контекстом."""
        follow_response = self.another_authorized.get(reverse('follow_index'))
        unfollow_response = self.third_authorized.get(reverse('follow_index'))
        expect_post = follow_response.context['page'][0]
        self.assertEqual(expect_post, self.post)
        self.assertNotIn(self.post, unfollow_response.context['page'])
        self.third_authorized.get(reverse('profile_follow',
                                          kwargs={'username': 'TestUser'}))
        self.assertTrue(Follow.objects.filter(user=self.third_user,
                                              author=self.author).exists())
        self.third_authorized.get(reverse('profile_unfollow',
                                          kwargs={'username': 'TestUser'}))
        self.assertFalse(Follow.objects.filter(user=self.third_user,
                                               author=self.author).exists())
