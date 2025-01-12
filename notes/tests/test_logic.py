from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NoteHandlingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-test',
            author=cls.author
        )
        cls.another_user = User.objects.create(username='Другой Толстой')
        cls.new_data_of_note = {
            'title': 'Новый Заголовок',
            'text': 'Новый Текст',
            'slug': cls.note.slug
        }

    def test_anonymous_user_create_note(self):
        """Проверяет, может ли аноним создать заметку"""
        Note.objects.all().delete()
        # Создать заметку
        self.client.post(reverse('notes:add'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_another_author_edit_and_delete_note(self):
        """Проверяет, что пользователь не может редактировать
        чужие заметки и удалять их.
        """
        self.client.force_login(self.another_user)
        response = self.client.post(reverse(
            'notes:edit',
            args=(self.note.slug,)
        ),
            data=self.new_data_of_note
        )
        # Проверим, что возвращается 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверим, что заметка не изменилась
        is_edited_note = Note.objects.get(slug=self.note.slug)
        self.assertEqual(is_edited_note.text, self.note.text)
        self.assertEqual(is_edited_note.title, self.note.title)

        # Теперь проверим, что её нельзя удалить
        self.client.delete(reverse('notes:delete', args=(self.note.slug,)))
        self.assertEqual(Note.objects.count(), 1)

    def test_author_edit_and_delete_note(self):
        """Проверяет, что автор может редактировать
        свои заметки и удалять их.
        """
        self.client.force_login(self.author)
        response = self.client.post(reverse(
            'notes:edit',
            args=(self.note.slug,)
        ),
            data=self.new_data_of_note
        )
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, reverse('notes:success'))
        # Проверим, что заметка изменилась
        is_edited_note = Note.objects.get(slug=self.note.slug)
        self.assertEqual(is_edited_note.text, self.new_data_of_note['text'])
        self.assertEqual(is_edited_note.title, self.new_data_of_note['title'])

        # Теперь проверим, что запись можно удалить
        self.client.delete(reverse('notes:delete', args=(self.note.slug,)))
        self.assertEqual(Note.objects.count(), 0)
