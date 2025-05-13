import requests
from flask_restful import reqparse, abort, Resource
from flask import jsonify
from data.db_classes import Works, TestAsks, Answers
from data.db_session import create_session


def abort_if_not_found(id, db_object, msg_obj=f"Object"):
    """ошибка для несуществующих объектов"""
    session = create_session()
    try:
        obj = session.query(db_object).get(id)
    except Exception:
        obj = False
    if not obj:
        abort(404, message=f'{msg_obj} is not found')


class WorkResource(Resource):
    def get(self, **kwargs):
        session = create_session()
        abort_if_not_found(kwargs['id'], Works, 'Work')
        works = session.query(Works).get(kwargs['id'])
        d = {}
        d['title'] = works.title
        d['tabletype'] = works.tabletype
        d['author_id'] = works.author_id
        d['ask_list'] = list(map(lambda ask: ask.id, works.asks))
        return jsonify(d)

    def post(self, **kwargs):
        session = create_session()
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True)
        parser.add_argument('tabletype', required=True)
        parser.add_argument('key', required=True)
        args = parser.parse_args()
        works = Works(
            title=args['title'],
            tabletype=args['tabletype'],
            author_id=int(args['key'])
        )
        session.add(works)
        session.commit()
        return jsonify({'id': works.id})




class AskResource(Resource):
    def get(self, **kwargs):
        session = create_session()
        abort_if_not_found(kwargs['id'], TestAsks, 'Ask')
        asks = session.query(TestAsks).get(kwargs['id'])
        d = {}
        if asks.is_private:  # is_private - флаг для заданий, к которым нельзя обратиться через api
            d['message'] = 'задание является приватным и недоступно через методы api'
        else:
            d['work_id'] = asks.work_id
            d['category'] = asks.category
            d['points'] = asks.points
            d['ask_text'] = asks.ask_text
            d['multimedia'] = asks.multimedia
            d['answers'] = list(map(lambda ans: ans.id, asks.answers))
            d['is_private'] = asks.is_private
            d['as_gia'] = asks.as_gia
        return jsonify(d)

    def post(self, **kwargs):
        session = create_session()
        parser = reqparse.RequestParser()
        parser.add_argument('work_id', required=True, type=int)
        parser.add_argument('ask_text', required=True)
        parser.add_argument('category', required=True)
        parser.add_argument('points', required=True)
        parser.add_argument('multimedia', required=False)
        parser.add_argument('as_gia', required=True, type=bool)
        parser.add_argument('is_private', required=True, type=bool)
        args = parser.parse_args()
        asks = TestAsks(
            work_id=args['work_id'],
            ask_text=args['ask_text'],
            category=args['category'],
            points=args['points'],
            multimedia=args['multimedia'],
            as_gia=args['as_gia'],
            is_private=args['is_private']
        )
        session.add(asks)
        session.commit()
        return jsonify({'id': asks.id})



class AnsResource(Resource):
    def get(self, **kwargs):
        session = create_session()
        abort_if_not_found(kwargs['id'], Answers, 'Answer')
        ans = session.query(Answers).get(kwargs['id'])
        d = {}
        d['ask_id'] = ans.ask_id
        d['is_cor'] = ans.is_cor
        d['ans_text'] = ans.ans_text
        return jsonify(d)

    def post(self, **kwargs):
        session = create_session()
        parser = reqparse.RequestParser()
        parser.add_argument('ans_text', required=True)
        parser.add_argument('is_cor', required=True, type=bool)
        parser.add_argument('ask_id', required=True, type=int)
        args = parser.parse_args()
        answers = Answers(
            ans_text=args['ans_text'],
            is_cor=args['is_cor'],
            ask_id=args['ask_id']
        )
        session.add(answers)
        session.commit()
        return jsonify({'id': answers.id})

# функции для работы с api:
url = 'http://127.0.0.1:5000/api/'
def create_api_work(key, title, tabletype='test'):  # key=id, tabletype пока только test
    """создание теста по api: key, title, tabletype=test"""
    global url
    dt_w = {}
    dt_w['key'] = key
    dt_w['title'] = title
    dt_w['tabletype'] = tabletype
    verd = requests.post(url=url + 'works/0', json=dt_w)
    return verd


def create_api_ask(work_id, ask_text, category, points, as_gia=False, is_private=False, multimedia=''):
    """создание вопроса по api: work_id, ask_text, category, points, as_gia=False, is_private=False, multimedia=''"""
    global url
    d = {}
    d['work_id'] = work_id
    d['ask_text'] = ask_text
    d['category'] = category
    d['points'] = points
    d['multimedia'] = multimedia
    d['as_gia'] = as_gia
    d['is_private'] = is_private
    verd = requests.post(url=url + 'testasks/0', json=d)
    return verd


def create_api_answer(ans_text, is_cor, ask_id):
    """создание ответа по api: ans_text, is_cor, ask_id"""
    global url
    d = {}
    d['ask_id'] = ask_id
    d['ans_text'] = ans_text
    d['is_cor'] = is_cor
    verd = requests.post(url=url + 'answers/0', json=d)
    return verd


def get_api_work(id):
    """получение теста по id"""
    global url
    d = requests.get(url + f'works/{id}').json()
    return d


def get_api_ask(id):
    """получение вопроса по id"""
    k = requests.get(url + f'testasks/{id}').json()
    return k


def get_api_answer(id):
    """получение ответа по id"""
    t = requests.get(url + f'answers/{id}').json()
    return t