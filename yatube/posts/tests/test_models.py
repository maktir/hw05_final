from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Group

User = get_user_model()


class PostModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст для теста. Это тест. Я тестирую.',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание для теста. Я все еще тестирую.',
        )

    def test_text_convert_to_string(self):
        post = PostModelsTest.post
        expected_text = post.text[:15]
        self.assertEqual(expected_text, str(post))

    def test_group_title(self):
        group = PostModelsTest.group
        expected_text = group.title
        self.assertEqual(expected_text, str(group))
