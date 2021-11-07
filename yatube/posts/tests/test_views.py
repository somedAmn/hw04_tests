from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import PAGINATOR_COUNT

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.another_author = User.objects.create_user(
            username='test-another_author'
        )
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description'
        )
        cls.post_without_group = Post.objects.create(
            text='test-text_without_group',
            author=cls.author
        )
        cls.post_with_group = Post.objects.create(
            text='test-text_with_group',
            author=cls.author,
            group=cls.group
        )
        cls.post_another_author = Post.objects.create(
            text='test-text_another_author',
            author=cls.another_author
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post_without_group.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post_without_group.pk}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]

        self.assertIn(
            first_object.text,
            ['test-text_without_group', 'test-text_with_group',
                'test-text_another_author']
        )
        self.assertIn(
            first_object.author,
            [self.author, self.another_author]
        )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        group = response.context['group']
        first_object = response.context['page_obj'][0]

        self.assertEqual(first_object.text, 'test-text_with_group')
        self.assertEqual(first_object.author, self.author)
        self.assertEqual(group, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.another_author.username}
            )
        )
        first_object = response.context['page_obj'][0]
        profile = response.context['profile']
        post_count = response.context['post_count']

        self.assertEqual(first_object.text, 'test-text_another_author')
        self.assertEqual(first_object.author, self.another_author)
        self.assertEqual(profile, self.another_author)
        self.assertEqual(post_count, 1)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post_without_group.pk}
            )
        )
        post = response.context['post']
        profile = response.context['profile']

        self.assertEqual(post, self.post_without_group)
        self.assertEqual(profile, self.author)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post_without_group.pk}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description'
        )
        for i in range(PAGINATOR_COUNT + 3):
            Post.objects.create(
                text=f'test-text{i}',
                author=cls.author,
                group=cls.group
            )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), PAGINATOR_COUNT)

    def test_index_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), PAGINATOR_COUNT)

    def test_group_list_second_page_contains_three_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.username}
            )
        )
        self.assertEqual(len(response.context['page_obj']), PAGINATOR_COUNT)

    def test_profile_second_page_contains_three_records(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.username}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
