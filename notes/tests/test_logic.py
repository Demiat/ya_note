from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class NoteHandlingTest(TestCase):
    """Тесты для работы с заметками"""

    ADD_NOTE_PATH = reverse('notes:add')
    DEL_NOTE_PATH = 'notes:delete'
    EDIT_NOTE_PATH = 'notes:edit'
    SUCCESS_NOTE_PATH = reverse('notes:success')

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
            'slug': 'new-slug'
        }

    def test_anonymous_user_create_note(self):
        """Проверяет, может ли аноним создать заметку"""
        Note.objects.all().delete()  # Почистимся от общей фикстуры
        response = self.client.post(
            self.ADD_NOTE_PATH, data=self.new_data_of_note
        )
        # Проверим редирект на логин
        expected_url = f'{reverse("users:login")}?next={self.ADD_NOTE_PATH}'
        self.assertRedirects(response, expected_url)
        # Проверим, что база пустая
        self.assertEqual(Note.objects.count(), 0)

    def test_login_user_create_note(self):
        """Проверяет, может ли пользователь создать заметку"""
        Note.objects.all().delete()  # Почистимся от общей фикстуры
        self.client.force_login(self.another_user)
        response = self.client.post(
            self.ADD_NOTE_PATH, data=self.new_data_of_note
        )
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.SUCCESS_NOTE_PATH)
        # Проверим, что появилась запись
        self.assertEqual(Note.objects.count(), 1)

    def test_another_author_edit_and_delete_note(self):
        """Проверяет, что пользователь не может редактировать
        чужие заметки и удалять их.
        """
        self.client.force_login(self.another_user)
        response = self.client.post(reverse(
            self.EDIT_NOTE_PATH,
            args=(self.note.slug,)
        ),
            data=self.new_data_of_note
        )
        # Проверим, что возвращается 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверим, что заметка не изменилась
        is_edited_note = Note.objects.get()
        self.assertEqual(is_edited_note.text, self.note.text)
        self.assertEqual(is_edited_note.title, self.note.title)
        self.assertEqual(is_edited_note.slug, self.note.slug)

        # Теперь проверим, что её нельзя удалить
        self.client.delete(reverse(self.DEL_NOTE_PATH, args=(self.note.slug,)))
        self.assertEqual(Note.objects.count(), 1)

    def test_author_edit_and_delete_note(self):
        """Проверяет, что автор может редактировать
        свои заметки и удалять их.
        """
        self.client.force_login(self.author)
        response = self.client.post(reverse(
            self.EDIT_NOTE_PATH,
            args=(self.note.slug,)
        ),
            data=self.new_data_of_note
        )
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.SUCCESS_NOTE_PATH)
        # Проверим, что заметка изменилась
        is_edited_note = Note.objects.get()
        self.assertEqual(is_edited_note.text, self.new_data_of_note['text'])
        self.assertEqual(is_edited_note.title, self.new_data_of_note['title'])
        self.assertEqual(is_edited_note.slug, self.new_data_of_note['slug'])

        # Теперь проверим, что запись можно удалить
        self.client.delete(
            reverse(self.DEL_NOTE_PATH, args=(is_edited_note.slug,))
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        """Не может быть двух записей с одинаковым slug"""
        self.new_data_of_note['slug'] = self.note.slug
        self.client.force_login(self.author)
        response = self.client.post(
            self.ADD_NOTE_PATH,
            data=self.new_data_of_note
        )
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        # Заметка должна остаться одна
        assert Note.objects.count() == 1
