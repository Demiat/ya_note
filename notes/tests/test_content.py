from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тесты для проверки работы контента"""

    @classmethod
    def setUpTestData(cls):
        # Создадим формы
        cls.form = NoteForm(data={'title': 'Это тест', 'text': 'test'})
        cls.form2 = NoteForm(data={
            'title': 'Это тест 2',
            'text': 'test 2',
            'slug': 'Проверим большой слаг 123' * 100
        })
        # Создадим заметки для автора и для других пользователей
        cls.author = User.objects.create(username='Lion-T')
        cls.another_user = User.objects.create(username='Another-Lion')
        for user in (cls.author, cls.another_user):
            Note.objects.create(
                title=f'Заметка of {user}',
                text='Текст заметки',
                author=user,
                slug=f'slug-note-of-{user}'
            )

    def test_form(self):
        """Проверяет работу формы"""
        self.assertEqual(self.form.is_valid(), True)
        # Форма2 с таким слагом не должна пройти
        self.assertEqual(self.form2.is_valid(), False)

        self.assertEqual(self.form.cleaned_data['title'], 'Это тест')
        self.assertEqual(self.form.cleaned_data['text'], 'test')
        # Проверим, что отсутствующий слаг заполняется сам
        test_slug = slugify('Это тест')
        self.assertEqual(self.form.cleaned_data['slug'], test_slug)

    def test_author_list_notes(self):
        """Проверяет, что автор может видеть только свои заметки в списке"""
        for user in (self.author, self.another_user):
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                # Поверим, что заметка попадает в список
                self.assertEqual(object_list[0].slug, f'slug-note-of-{user}')
                # Что она принадлежит автору
                self.assertEqual(object_list[0].author, user)

    def test_pages_contains_form(self):
        """Проверяет, что страницы содержат форму"""
        self.client.force_login(self.author)
        for page, arg in (
            ('notes:add', None),
            ('notes:edit', (f'slug-note-of-{self.author}',))
        ):
            with self.subTest(url=page):
                response = self.client.get(reverse(page, args=arg))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
