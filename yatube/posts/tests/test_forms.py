from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404

from posts.models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description'
        )
        cls.post = Post.objects.create(
            text='test-text',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_post_create_authorized_user(self):
        form_data = {
            'text': 'test-create_text'
        }
        self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        created_post = get_object_or_404(Post, text=form_data['text'], author=self.author)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, self.author)

    def test_post_edit_author(self):
        form_data = {
            'text': 'test-update_text'
        }
        self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        updated_post = get_object_or_404(Post, pk=PostFormTests.post.pk)
        self.assertEqual(updated_post.text, form_data['text'])
        self.assertEqual(updated_post.author, self.author)

    def test_post_create_guest_user(self):
        form_data = {
            'text': 'test-guest_text'
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.filter(text=form_data['text'])
        self.assertFalse(post.exists())

    def test_post_edit_guest_user(self):
        form_data = {
            'text': 'test-guest_update_text'
        }
        self.client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )
        post = get_object_or_404(Post, pk=PostFormTests.post.pk)
        self.assertNotEqual(post.text, form_data['text'])