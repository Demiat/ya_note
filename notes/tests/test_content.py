from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создадим форму
        cls.form = NoteForm(data={'title': 'Это тест', 'text': 'test'})
        cls.form2 = NoteForm(data={
            'title': 'Это тест',
            'text': 'test',
            'slug': 'Проверим большой слаг 123' * 100
        })
        # Создадим заметки для автора и для других пользователей
        cls.author = User.objects.create(username='Lion-T')
        cls.another_user = User.objects.create(username='Another-Lion')
        for user in (cls.author, cls.another_user):
            Note.objects.bulk_create(
                Note(
                    title=f'Заметка {index} of {user}',
                    text='Текст заметки',
                    author=user,
                    slug=f'slug-{index}-of-{user}'
                ) for index in range(5)
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
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        authors = [note.author for note in object_list]
        for author in authors:
            self.assertEqual(author, self.author)
        self.assertIn(self.another_user, object_list)
