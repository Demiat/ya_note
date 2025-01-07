from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.Note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zag-test',
            author=cls.author)
        cls.another_user = User.objects.create(username='Другой Толстой')
        cls.args = ('zag-test',)
        cls.urls = (
            ('notes:home', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', cls.args),
            ('notes:edit', cls.args),
            ('notes:delete', cls.args),
        )

    def test_pages_availability_for_anonymous(self):
        """Тестирует доступ анонима к страницам"""
        for reverse_name, args in self.urls[:1]:
            with self.subTest(name=reverse_name):
                url = reverse(reverse_name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Тестирует редирект анонима на страницу авторизации"""
        login_url = reverse('users:login')
        for reverse_name, args in self.urls[1:]:
            with self.subTest(name=reverse_name):
                url = reverse(reverse_name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self):
        """Тестирует доступ пользователей к чужим ресурсам"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for reverse_name, args in self.urls[5:]:
                with self.subTest(user=user, name=reverse_name):
                    url = reverse(reverse_name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
