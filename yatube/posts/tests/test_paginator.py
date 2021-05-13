from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username='PaginatorUser')
        cls.group = Group.objects.create(title='TestTitle',
                                         slug='test-slug')
        cls.post = Post.objects.create(
            text='TestText',
            group=cls.group,
            author=cls.user)
        for post in range(12):
            Post.objects.create(
                text='TestText',
                group=cls.group,
                author=cls.user
            )

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_first_group_page_contains_ten_records(self):
        response = self.client.get(reverse('group_posts',
                                           kwargs={'slug': 'test-slug'}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_group_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('group_posts',
                                           kwargs={'slug': 'test-slug'})
                                   + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
