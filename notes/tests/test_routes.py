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

    def test_pages_availability_for_anonymous(self):
        urls = (
            ('notes:home', None, HTTPStatus.OK),
            ('notes:list', None, HTTPStatus.FOUND),
            ('notes:add', None, HTTPStatus.FOUND),
            ('notes:success', None, HTTPStatus.FOUND),
        )
        for reverse_name, args, status in urls:
            with self.subTest(name=reverse_name):
                url = reverse(reverse_name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for reverse_name in (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        ):
            with self.subTest(name=reverse_name):
                url = reverse(reverse_name, args=('zag-test',))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    
    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for reverse_name in ('notes:edit', 'notes:delete'):  
                with self.subTest(user=user, name=reverse_name):        
                    url = reverse(reverse_name, args=('zag-test',))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
