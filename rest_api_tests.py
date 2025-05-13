import pytest
from rest_api import get_api_work, get_api_ask, get_api_answer, create_api_answer, create_api_work, create_api_ask


# API покрыто тестами:
# все хорошо
def test_create_work_cor():  # разделить на отдельные функции нельзя, т.к. нужно хранить id
    w = create_api_work(1, 'api_cor')
    id_w = w.json()['id']
    assert type(id_w) is int
    a = create_api_ask(id_w, '2+2', 'Математика', 1, False, False, 'https://www.wolframalpha.com/')
    id_a = a.json()['id']
    assert type(id_a) is int
    ans1 = create_api_answer(4, True, id_a)
    id_an = ans1.json()['id']
    assert type(id_an) is int


def test_get_ask_cor_private():
    a = create_api_ask(4, 'Приватный', 'Другое', 1, False, True)
    assert get_api_ask(a.json()['id']) == {'message': 'задание является приватным и недоступно через методы api'}


def test_get_ask_cor_public():
    a = create_api_ask(4, 'Открытый', 'Другое', 1, False, False)
    assert get_api_ask(a.json()['id']) == {'answers': [], 'as_gia': False, 'ask_text': 'Открытый', 'category': 'Другое',
                                           'is_private': False, 'multimedia': '', 'points': 1, 'work_id': 4}


def test_get_answer_cor():
    q = create_api_ask(4, 'Открытый', 'Другое', 1, False, False)
    a = create_api_answer('Ответ', True, q.json()['id'])
    assert get_api_answer(a.json()['id']) == {'ans_text': 'Ответ', 'ask_id': q.json()['id'], 'is_cor': True}


def test_get_work_cor():
    q = create_api_work(1, 'api_cor')
    assert get_api_work(q.json()['id']) == {'ask_list': [], 'author_id': 1, 'tabletype': 'test', 'title': 'api_cor'}


#  объект не существует
def test_get_work_not_found():
    assert get_api_work(0) == {'message': 'Work is not found'}


def test_get_ask_not_found():
    assert get_api_ask(0) == {'message': 'Ask is not found'}


def test_get_answer_not_found():
    assert get_api_answer(0) == {'message': 'Answer is not found'}
