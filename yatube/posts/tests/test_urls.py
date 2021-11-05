from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.user = User.objects.create_user(username='test-user')
        cls.post = Post.objects.create(
            text='test-text',
            author=cls.author
        )
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description'
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_unexisting_url_at_desired_location(self):
        """Несуществующая страница выдаёт ошибку 404."""
        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_posts_index_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница profile/test-user/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/test-user/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail_url_exists_at_desired_location(self):
        """Страница posts/<post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(
            f'/posts/{PostURLTests.post.pk}/', follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница posts/<post_id>/edit доступна автору поста."""
        response = self.author_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/', follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_post_create_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_post_edit_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /posts/<post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{PostURLTests.post.pk}/edit/'
        )

    def test_post_edit_url_redirect_no_author_on_post_detail(self):
        """Страница по адресу /posts/<post_id>/edit/ перенаправит не автора
        на подробное описание поста.
        """
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{PostURLTests.post.pk}/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test-user/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)
