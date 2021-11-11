from django.test import Client, TestCase
from django.urls import reverse_lazy
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author(self):
        """Проверка доступности адреса /about/author/."""
        response = self.guest_client.get(reverse_lazy('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        """Проверка доступности адреса /about/tech/."""
        response = self.guest_client.get(reverse_lazy('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
