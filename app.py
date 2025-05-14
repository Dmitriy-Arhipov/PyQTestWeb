import json
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from data.db_session import create_session, global_init
from data.db_classes import Users, Works, Results, TestAsks, Answers
from data.forms import LoginForm, RegisterForm, TestForm, SearchTestForm, AskForm, NumForm, AnswerForm, AnsList
from rest_api import WorkResource, AskResource, AnsResource
import logging

logger = logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'PyQTest_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

global_init("data/PyQTest.db")
db_sess = create_session()

@login_manager.user_loader
def load_user(user_id):
    """добавление пользователя"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    return db_sess.query(Users).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """авторизация"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(f"/lk/{current_user.id}")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    """выход"""
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """регистрация"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = Users(
            surname=form.surname.data,
            name=form.name.data,
            fathername=form.fathername.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/lk/<int:user_id>')
@login_required
def lk(user_id):
    """личный кабинет"""
    return render_template("lk.html", title='Личный кабинет', user_id=user_id)


@app.route('/')
@app.route('/info')
def info():
    """информация о системе"""
    return render_template("info.html", title='О системе')


@app.route('/create/<int:user_id>', methods=['GET', 'POST'])
@login_required
def create(user_id):
    """создание работы"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    form = TestForm()
    if form.validate_on_submit():
        work = Works(
            author=current_user,
            tabletype='test',
            title=str(form.title.data)
        )
        db_sess.add(work)
        db_sess.commit()
        return redirect(f'/edit/{user_id}/{work.id}')
    return render_template("create.html", form=form, user_id=user_id)


@app.route('/edit/<int:user_id>/<int:work_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id, work_id):
    """редактирование работы"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    w = db_sess.query(Works).filter(Works.id == work_id)[0]
    if w.author_id != user_id:
        return 'Ошибка доступа: Вы не можете редактировать этот тест'
    ask_id_lst = list(map(lambda t: t.id, w.asks))
    numform = NumForm()
    if numform.validate_on_submit() and int(numform.ans_count.data) > 0:
        with open('globals.json') as f:
            d = json.load(f)
        d['ans_count'] = str(numform.ans_count.data)
        with open('globals.json', 'w') as f:
            json.dump(d, f)
        return redirect(f'/create/testask/{user_id}/{work_id}')
    return render_template("edit.html", nform=numform, user_id=user_id, work_id=work_id, ask_id_lst=ask_id_lst)


@app.route('/create/testask/<int:user_id>/<int:work_id>', methods=['GET', 'POST'])
@login_required
def create_testask(user_id, work_id):
    """создание вопроса"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    with open('globals.json') as f:  # работа с файлами: вместо глобальной переменной json-объект
        d = json.load(f)
    form = AskForm()
    if 'ans_count' in d.keys():
        for i in range(int(d['ans_count'])):
            form.answers.append_entry(AnswerForm)
    if form.validate_on_submit():
        ask = TestAsks(
            work_id=work_id,
            ask_text=str(form.ask_text.data),
            category=str(form.category.data),
            points=int(form.points.data),
            multimedia=str(form.multimedia.data),
            as_gia=bool(form.as_gia.data),
            is_private=bool(form.is_private.data)
        )
        for answr in form.answers.data:
            if type(answr['ans_text']) is str:
                ans = Answers(
                    ask=ask,
                    ans_text=str(answr['ans_text']),
                    is_cor=(str(answr['cor']) == 'True')
                )
                db_sess.add(ans)
        db_sess.add(ask)
        db_sess.commit()
        return redirect(f'/edit/testask/{user_id}/{work_id}/{ask.id}')
    def_dict = {'ask_text': '', 'multimedia': '', 'category': '', 'points': ''}
    return render_template("create_testask.html", form=form, user_id=user_id, work_id=work_id, n=int(d['ans_count']),
                           def_dict=def_dict, str=str)


@app.route('/edit/testask/<int:user_id>/<int:work_id>/<int:ask_id>', methods=['GET', 'POST'])
@login_required
def edit_testask(user_id, work_id, ask_id):
    """редактирование вопроса"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    w = db_sess.query(Works).filter(Works.id == work_id)[0]
    if w.author_id != user_id:
        return 'Ошибка доступа: Вы не можете редактировать этот тест'
    ask = db_sess.query(TestAsks).filter(TestAsks.id == ask_id)[0]
    form = AskForm()
    def_dict = {}
    def_dict['ask_text'] = ask.ask_text
    def_dict['multimedia'] = ask.multimedia
    def_dict['category'] = ask.category
    def_dict['points'] = ask.points
    def_dict['is_private'] = ask.is_private
    def_dict['as_gia'] = ask.as_gia
    for i in range(len(ask.answers)):
        f = AnswerForm()
        form.answers.append_entry(f)
        form.answers[i]['ans_text'].default = ask.answers[i].ans_text
        form.answers[i]['cor'].default = str(ask.answers[i].is_cor)

    if form.multimedia.default is None:
        form.multimedia.default = ''
    if form.ask_text.default is None:
        form.ask_text.default = ''
    if form.validate_on_submit():
        db_sess.query(TestAsks).filter(TestAsks.id == ask_id).update({
            TestAsks.ask_text: str(form.ask_text.data) if form.ask_text.data else form.ask_text.default,
            TestAsks.category: str(form.category.data) if form.category.data else form.category.default,
            TestAsks.points: int(form.points.data) if form.points.data else form.points.default,
            TestAsks.multimedia: str(form.multimedia.data) if form.multimedia.data else form.multimedia.default,
            TestAsks.is_private: bool(form.is_private.data),
            TestAsks.as_gia: bool(form.as_gia.data)
        })
        ask = db_sess.query(TestAsks).filter(TestAsks.id == ask_id)
        for i in range(len(ask[0].answers)):
            is_cor = str(form.answers.data[i]['cor']) == 'True'
            db_sess.query(Answers).filter(Answers.id == ask[0].answers[i].id).update({
                Answers.ans_text: str(form.answers.data[i]['ans_text']) if form.answers.data[i]['ans_text'] else
                form.answers[i]['ans_text'].default,
                Answers.is_cor: is_cor
            })
        db_sess.commit()
        return redirect(f'/edit/testask/{user_id}/{work_id}/{ask_id}')
    return render_template("create_testask.html", form=form, user_id=user_id, work_id=work_id, ask_id=ask_id, none=None,
                           n=len(ask.answers), def_dict=def_dict, str=str)


@app.route('/search/<int:user_id>', methods=['GET', 'POST'])
@login_required
def search(user_id):
    """поиск теста по id"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    form = SearchTestForm()
    works = []
    if form.validate_on_submit():
        if int(form.work_id.data) > 0:
            if list(db_sess.query(Works).filter(Works.id == form.work_id.data)):
                return redirect(f'/run/{user_id}/{form.work_id.data}')
            else:
                pass
        else:
            if not form.fio.data or not form.title.data:
                pass
            else:
                fio = form.fio.data.split(' ')
                user = db_sess.query(Users).filter(Users.surname == fio[0], Users.name == fio[1],
                                                   Users.fathername == fio[2])
                if list(user):
                    works = db_sess.query(Works).filter(Works.title == form.title.data, Works.author_id == user[0].id)
                else:
                    pass
    return render_template("search.html", form=form, user_id=user_id, works=works)


@app.route('/run/<int:user_id>/<int:work_id>', methods=['GET', 'POST'])
@login_required
def run(user_id, work_id):
    """запуск в пользовательском режиме всего теста"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    asks = db_sess.query(TestAsks).filter(TestAsks.work_id == work_id)
    return redirect(f'/run/testask/{user_id}/{work_id}/{asks[0].id}')


@app.route('/run/testask/<int:user_id>/<int:work_id>/<int:ask_id>', methods=['GET', 'POST'])
@login_required
def run_testask(user_id, work_id, ask_id):
    """запуск в пользовательском режиме отдельного вопроса"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    asks = list(db_sess.query(TestAsks).filter(TestAsks.work_id == work_id))
    ask_id_lst = list(map(lambda t: t.id, asks))
    cur_ask = db_sess.query(TestAsks).filter(TestAsks.id == ask_id)[0]
    answers = list(map(lambda answer: answer.ans_text, cur_ask.answers))
    res = db_sess.query(Results).filter(Results.ask_id == ask_id, Results.work_id == work_id,
                                        Results.student_id == user_id)
    if list(res):
        selected = res[0].selected.split(';')
        if selected[0] == '':
            selected = []
        else:
            selected = map(int, res[0].selected.split(';'))
        defaults = [cur_ask.answers[i].id in selected for i in range(len(answers))]
    else:
        defaults = [False for i in range(len(answers))]
    form = AnsList(answers, defaults)
    names = [(f'ans{i}', cur_ask.answers[i].ans_text) for i in range(len(cur_ask.answers))]
    if form.validate_on_submit():
        cor_cnt, sel = 0, []
        for i in range(len(cur_ask.answers)):
            ans = cur_ask.answers[i]
            if str(form[f'ans{i}'].data) == str(ans.is_cor):
                cor_cnt += 1
            if form[f'ans{i}'].data:
                sel.append(str(ans.id))
        # две системы оценивания:
        # по умолчанию - начисление баллов за каждое совпадение: верный отмеченный или неверный неотмеченный
        # as_gia - "все или ничего", никаких частичных баллов
        points = (cor_cnt == len(cur_ask.answers)) * cur_ask.points if cur_ask.as_gia else (cor_cnt / len(
            cur_ask.answers)) * cur_ask.points
        if list(res):
            res.update({
                Results.points: points,
                Results.selected: ';'.join(sel)
            })
        else:
            result = Results(
                student_id=user_id,
                work_id=work_id,
                ask_id=ask_id,
                points=points,
                selected=';'.join(sel)
            )
            db_sess.add(result)
        db_sess.commit()
    return render_template("run_testask.html", title='Выполнение теста', ask_id_lst=ask_id_lst, ask=cur_ask, form=form,
                           user_id=user_id, work_id=work_id, names=names)


@app.route('/lk/tests/<int:user_id>')
@login_required
def mytests(user_id):
    """список тестов"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    tests = db_sess.query(Works).filter(Works.author_id == user_id)
    return render_template("tests.html", title='Мои тесты', user_id=user_id, tests=tests)


@app.route('/results/<int:work_id>')
@login_required
def results(work_id):
    """результаты учеников"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    res_lst = db_sess.query(Results).filter(Results.work_id == work_id)
    res_studs = {}
    for res in res_lst:
        student = ' '.join([res.student.surname, res.student.name, res.student.fathername])
        if student in res_studs.keys():
            res_studs[student].append((res.ask.ask_text, round(res.points, 3), res.ask.points))
        else:
            res_studs[student] = [(res.ask.ask_text, round(res.points, 3), res.ask.points)]
    return render_template("results.html", title='Мои тесты', work_id=work_id, results=res_studs)


@app.route('/lk/results/<int:user_id>')
@login_required
def myresults(user_id):
    """результаты самого пользователя"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    res_lst = db_sess.query(Results).filter(Results.student_id == user_id)
    res_works = {}
    for res in res_lst:
        if res.work:
            author = ' '.join([res.work.author.surname, res.work.author.name, res.work.author.fathername])
            if (res.work.title, author, res.work.id) in res_works.keys():
                res_works[(res.work.title, author, res.work.id)].append(
                    (res.ask.ask_text, round(res.points, 3), res.ask.points))
            else:
                res_works[(res.work.title, author, res.work.id)] = [
                    (res.ask.ask_text, round(res.points, 3), res.ask.points)]
    return render_template("myresults.html", title='Мои результаты', user_id=user_id, results=res_works)


@app.route('/delete/<int:user_id>/<int:work_id>', methods=['GET', 'POST'])
@login_required
def delete(user_id, work_id):
    """удаление теста"""
    global db_sess
    if not db_sess:
        global_init("data/PyQTest.db")
        db_sess = create_session()
    work = db_sess.query(Works).filter(Works.id == work_id)
    if work[0].author_id == user_id:
        db_sess.delete(work[0])
        db_sess.commit()
        return redirect(f'/lk/tests/{user_id}')
    return 'Ошибка доступа: Вы не можете удалить этот тест'


def main():
    api.add_resource(WorkResource, '/api/works/<int:id>')
    api.add_resource(AskResource, '/api/testasks/<int:id>')
    api.add_resource(AnsResource, '/api/answers/<int:id>')

    app.run()


if __name__ == '__main__':
    main()
