from django.test import TestCase, Client
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from http import HTTPStatus
from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/unexisting_page/': 'core/404.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_author.get(adress)
                self.assertTemplateUsed(response, template)

    def test_homepage(self):
        """Проверка доступности всем адреса /."""
        response = self.guest_client.get(reverse_lazy('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list(self):
        """Проверка доступности всем адреса /group/<slug:slug>/."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile(self):
        """Проверка доступности всем адреса /profile/<str:username>/."""
        response = self.guest_client.get(f'/profile/{self.user}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail(self):
        """Проверка доступности всем адреса /posts/<int:post_id>/."""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Проверка несуществующего адреса /unexisting_page/."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_post(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_edit_post(self):
        """Страница /posts/<post.id>/edit/ доступна авторизованному автору."""
        adress = f'/posts/{self.post.id}/edit/'
        response = self.authorized_author.get(adress)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_redirect_anonymous_on_auth_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def test_create_edit_post_url_redirect_anonymous_on_auth_login(self):
        """Страница /posts/<post.id>/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        adress = (f'/posts/{self.post.id}/edit/')
        response = self.guest_client.get(adress, follow=True)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/edit/'))
