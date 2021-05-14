from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from posts.models import Post, Group, Follow

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testusername')
        cls.another_user = User.objects.create_user(username='anotheruser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.group = Group.objects.create(
            title='testgroup',
            description='testdescription',
            slug='test-slug',
        )
        cls.templates_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/new/': 'new.html',
            '/testusername/': 'profile.html',
            '/testusername/1/': 'post.html',
            '/testusername/1/edit/': 'new.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized = Client()
        self.another_authorized.force_login(self.another_user)

    def test_urls_exists_at_desired_location(self):
        """Страницы urls доступны любому пользователю."""
        urls = ['/',
                '/group/test-slug/',
                ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_url_exists_at_desired_location(self):
        """Страницы urls доступны авторизованному пользователю."""
        urls = ['/new/',
                '/testusername/',
                '/testusername/1/',
                ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_url_redirect_anonymous(self):
        """
        Страницы urls перенаправляют анонимного пользователя на redirections.
        """
        urls_redirections = {
            '/new/': '/auth/login/?next=/new/',
            '/testusername/1/edit/': ('/auth/login/?next='
                                      '/testusername/1/edit/'),
            '/anotheruser/follow/': ('/auth/login/?next='
                                     '/anotheruser/follow/'),
            '/anotheruser/unfollow/': ('/auth/login/?next='
                                       '/anotheruser/unfollow/'),
        }
        for url, redirection in urls_redirections.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, redirection)

    def test_closed_access_to_edit_anonymous(self):
        """
        Страница /edit/ недоступна неавторизованному пользователю.
        """
        response = self.guest_client.get('/testusername/1/edit/')
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_closed_access_to_edit_not_author(self):
        """Страница /edit/ недоступна не автору записи."""
        response = self.another_authorized.get('/testusername/1/edit/')
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('post', kwargs={
            'username': 'testusername',
            'post_id': 1
        }))

    def test_open_access_to_edit_by_author(self):
        """Страница /edit/ доступна автору записи."""
        response = self.authorized_client.get('/testusername/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_pages(self):
        """
        Зарегистрированный пользователь после подписки перенаправляется
        на страницу подписок.
        """
        response = self.authorized_client.get(reverse('profile_follow',
                                                      kwargs={
                                                          'username': (
                                                              'anotheruser'
                                                          )
                                                      }
                                                      )
                                              )
        self.assertRedirects(response, reverse('follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unfollow_pages(self):
        """
        Зарегистрированный пользователь после отписки перенаправляется
        на страницу подписок.
        """
        Follow.objects.create(user=self.user, author=self.another_user)
        response = self.authorized_client.get(reverse('profile_unfollow',
                                                      kwargs={
                                                          'username': (
                                                              'anotheruser'
                                                          )
                                                      }
                                                      )
                                              )
        self.assertRedirects(response, reverse('follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for adress, template in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_not_found(self):
        response = self.guest_client.get('/wrong_url/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
