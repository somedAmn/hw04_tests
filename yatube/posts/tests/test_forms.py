from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        Post.objects.create(
            text='test-text',
            author=cls.author,
            pk=1
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create_if_valid(self):
        initially_count = Post.objects.count()
        form_data = {
            'text': 'test-text'
        }
        self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(Post.objects.count(), initially_count)

    def test_post_edit(self):
        form_data = {
            'text': 'test-text_upd'
        }
        self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertEqual(str(Post.objects.get(pk=1)), 'test-text_upd')
