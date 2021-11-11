import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

small_gif = ( 
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
uploaded = SimpleUploadedFile(
    name='small.gif',
    content=small_gif,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
            text='Тестовая запись',
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый коммент',
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def check_post(self, post):
        """Метод помогает тестировать наполнение поста"""
        self.assertEqual(post.group, PostPagesTests.group)
        self.assertEqual(post.text, PostPagesTests.post.text)
        self.assertEqual(post.author, PostPagesTests.user)
        self.assertEqual(post.image, PostPagesTests.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'auth'}): (
                'posts/profile.html'
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}): (
                    'posts/post_detail.html'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}): (
                    'posts/create_post.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        cache.clear()
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Посты на странице index наполнены корректно."""
        cache.clear()
        response = self.authorized_author.get(reverse('posts:index'))
        post_list = response.context.get('posts')
        post = post_list[0]
        self.check_post(post)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        group_title = response.context.get('group').title
        group_description = response.context.get('group').description
        group_slug = response.context.get('group').slug
        post = response.context['posts'][0]
        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_description, 'Тестовое описание')
        self.assertEqual(group_slug, 'test-slug')
        self.check_post(post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        username = response.context.get('username').username
        count_posts = response.context.get('count_posts')
        post = response.context['page_obj'][0]
        self.assertEqual(username, 'auth')
        self.assertEqual(count_posts, 1)
        self.check_post(post)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}))
        post = response.context.get('post_detail')
        count_posts = response.context.get('count_posts')
        comments = response.context.get('comments')
        count_comments = len(comments)
        self.check_post(post)
        self.assertEqual(count_posts, 1)
        self.assertEqual(count_comments, 1)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class CachePostPagesTests(TestCase):
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
            text='Тестовая запись',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_caching(self):
        """Проверка кэша Главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        content_before = response.content

        self.post.delete()

        response = self.authorized_client.get(reverse('posts:index'))
        content_after = response.content
        self.assertEqual(content_after, content_before)

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        content_after = response.content
        self.assertNotEqual(content_after, content_before)


class PaginatorPostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        number_of_posts = 14
        for i in range(number_of_posts):
            cls.post = Post.objects.create(
                author=cls.user,
                text=(f'Запись {i}'),
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_first_page_posts_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10"""
        cache.clear()
        response = self.authorized_author.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_posts_contains_four_records(self):
        """Проверка: количество постов на второй странице равно 4"""
        cache.clear()
        response = self.authorized_author.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_first_page_group_list_posts_contains_ten_records(self):
        """Проверка group_list:
        количество постов на первой странице равно 10
        """
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_posts_contains_four_records(self):
        """Проверка group_list: количество постов на второй странице равно 4"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_first_page_profile_posts_contains_ten_records(self):
        """Проверка profile: количество постов на первой странице равно 10"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_posts_contains_four_records(self):
        """Проверка profile: количество постов на второй странице равно 4"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)


class FollowTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='Follower')
        self.user2 = User.objects.create_user(username='Unfollower')
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2.force_login(self.user2)
        self.author = User.objects.create_user(username='author')

    def test_follow(self):
        """Новый автор добавляется."""
        follow = Follow.objects.count()
        self.assertTrue(self.authorized_client1.get(
            reverse('posts:profile_follow', args={self.author}))
        )
        self.assertEqual(Follow.objects.count(), follow + 1)
        last_follow = Follow.objects.latest('id')
        self.assertEqual(last_follow.author_id, self.author.id)
        self.assertEqual(last_follow.user_id, self.user1.id)

    def test_unfollow(self):
        """Автор удаляется."""
        follow = Follow.objects.count()
        self.assertTrue(self.authorized_client1.get(
            reverse('posts:profile_unfollow', args={self.author}))
        )
        self.assertEqual(Follow.objects.count(), follow)

    def test_post_for_followers(self):
        """Новый пост автора появляется в ленте Follower
        и не появляется в ленте Unfollower.
        """
        post = Post.objects.create(
            author=self.author,
            text='Тестовая запись',
        )

        Follow.objects.create(
            user=self.user1,
            author=self.author,
        )
        response1 = self.authorized_client1.get(reverse('posts:follow_index'))
        first_object = response1.context['page_obj'][0]
        response2 = self.authorized_client2.get(reverse('posts:follow_index'))
        posts = response2.context['page_obj']
        self.assertEqual(first_object, post)
        self.assertEqual(len(posts), 0)
