from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='username')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test-slug',
            description='TestDescription'
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_cache(self):
        form_data = {
            'text': 'Brand new post for test',
            'group': self.group.id,
            'author': self.user,
        }
        self.client.post(
            reverse('new_post'),
            data=form_data,
            follow=True,
        )
        created_post = Post.objects.filter(
            text='Brand new post for test',
            author=self.user,
            group=self.group)
        response = self.client.get(reverse('index'))
        self.assertTrue(created_post.exists())
        created_post.delete()
        self.assertIn('Brand new post for test', response.content.decode())
