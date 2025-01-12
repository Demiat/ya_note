from notes.models import Note
from pytest import mark


def test_note_exists(note):
    notes_count = Note.objects.count()
    # Общее количество заметок в БД равно 1.
    assert notes_count == 1
    # Заголовок объекта, полученного при помощи фикстуры note,
    # совпадает с тем, что указан в фикстуре.
    assert note.title == 'Заголовок'


# Обозначаем, что тесту нужен доступ к БД.
# Без этой метки тест выдаст ошибку доступа к БД.
@mark.django_db
def test_empty_db():
    notes_count = Note.objects.count()
    # В пустой БД никаких заметок не будет:
    assert notes_count == 0
