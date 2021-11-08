from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

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
        last_created_post = Post.objects.order_by('-pk')[0]
        self.assertEqual(last_created_post.text, form_data['text'])
        self.assertEqual(last_created_post.author, self.author)

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
        count_before = Post.objects.count()
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        count_after = Post.objects.count()
        post = Post.objects.filter(text=form_data['text'])
        self.assertFalse(post.exists())
        self.assertEqual(count_before, count_after)

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

    def test_post_with_group_create_authorized_user(self):
        form_data = {
            'text': 'test-create_text_with_group',
            'group': PostFormTests.group.pk
        }
        self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_created_post = Post.objects.order_by('-pk')[0]
        self.assertEqual(last_created_post.text, form_data['text'])
        self.assertEqual(last_created_post.author, self.author)
        self.assertEqual(last_created_post.group, PostFormTests.group)

    def test_post_with_group_edit_author(self):
        form_data = {
            'text': 'test-update_text_with_group',
            'group': PostFormTests.group.pk
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
        self.assertEqual(updated_post.group, PostFormTests.group)
