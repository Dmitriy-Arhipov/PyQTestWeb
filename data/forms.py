from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, TextAreaField, StringField, SelectField, \
    FieldList, FormField, IntegerField
from wtforms.validators import DataRequired, ValidationError
from .db_session import create_session
from .db_classes import Users


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    fathername = StringField('Отчество (если есть)', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

    def validate_email(self, mail):
        """email должен быть уникальным"""
        db_sess = create_session()
        if db_sess.query(Users).filter(Users.email == mail.data).first() is not None:
            raise ValidationError('Данная почта уже зарегистрирована')


class AnswerForm(FlaskForm):
    class Meta:
        csrf = False

    ans_text = TextAreaField('Введите ответ', default='')
    cor = SelectField('Выберите тип', choices=[(True, 'Правильный'), (False, 'Ошибочный')], validate_choice=False)


class AskForm(FlaskForm):
    category = SelectField('Выберите категорию', choices=[
        ('Математика', 'Математика'),
        ('Физика', 'Физика'),
        ('Информатика', 'Информатика'),
        ('Химия', 'Химия'),
        ('Биология', 'Биология'),
        ('История', 'История'),
        ('Обществознание', 'Обществознание'),
        ('Русский язык', 'Русский язык'),
        ('Другое', 'Другое')
    ])
    ask_text = TextAreaField('Введите вопрос')
    multimedia = StringField('Cсылка на файл')
    points = IntegerField('Баллов за правильный ответ')
    answers = FieldList(FormField(AnswerForm))
    as_gia = BooleanField('Оценивать в формате ГИА (все или ничего)')
    is_private = BooleanField('Вопрос недоступен для API')
    submit = SubmitField('Сохранить')

    def validate_points(self, points):
        """Количество баллов должно быть натуральным"""
        if not points.data and not points.default:
            raise ValidationError
        if points.data and int(points.data) < 0:
            raise ValidationError('Введите натуральное число')


class TestForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()], default='Тест 1')
    submit = SubmitField('Сохранить')


class SearchTestForm(FlaskForm):
    fio = StringField('ФИО автора теста')
    title = StringField('Название теста')
    work_id = IntegerField('id теста, -1, если не знаете', default=-1)
    submit = SubmitField('Искать')


class NumForm(FlaskForm):
    ans_count = IntegerField('Сколько вариантов ответа', validators=[DataRequired()])
    submit = SubmitField('Добавить тестовый вопрос')

    def validate_ans_count(self, ans_count):
        if not ans_count.data and not ans_count.default:
            raise ValidationError
        if int(ans_count.data) < 0:
            raise ValidationError('Введите натуральное число')


# небольшое отступление от PEP8: функция - фабрика, возвращающая класс, поэтому именуется как класс
def AnsList(answers, defaults):
    class AnsListForm(FlaskForm):
        pass

    # параметры именуются "на лету", т.к. заранее не известно, сколько будет ответов

    for (i, ans) in enumerate(answers):
        setattr(AnsListForm, f'ans{i}', BooleanField(label=ans, default=defaults[i]))
    setattr(AnsListForm, 'submit', SubmitField('Сохранить'))
    return AnsListForm()
