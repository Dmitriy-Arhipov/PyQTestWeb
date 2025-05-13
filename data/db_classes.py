from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    surname = Column(String, nullable=True)
    name = Column(String, nullable=True)
    fathername = Column(String, default='')
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)
    works = orm.relationship("Works", back_populates='author')
    results = orm.relationship("Results", back_populates='student')

    def set_password(self, password):
        """в БД вместо пароля хранится его хэш"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """проверка хэша введенного пароля"""
        return check_password_hash(self.password, password)


class Works(SqlAlchemyBase):
    __tablename__ = 'works'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = orm.relationship('Users')
    tabletype = Column(String, nullable=True)
    title = Column(String, nullable=True)
    asks = orm.relationship("TestAsks", back_populates='work')
    results = orm.relationship("Results", back_populates='work')


class Results(SqlAlchemyBase):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    student = orm.relationship('Users')
    work_id = Column(Integer, ForeignKey("works.id"))
    work = orm.relationship('Works')
    ask_id = Column(Integer, ForeignKey("testasks.id"))
    ask = orm.relationship('TestAsks')
    points = Column(Integer)
    selected = Column(String, default='')


class TestAsks(SqlAlchemyBase):
    __tablename__ = 'testasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_id = Column(Integer, ForeignKey("works.id"))
    work = orm.relationship('Works')
    ask_text = Column(String, nullable=True)
    category = Column(String, default='Другое')
    points = Column(Integer)
    multimedia = Column(String, nullable=False)
    answers = orm.relationship("Answers", back_populates='ask')
    is_private = Column(Boolean, default=False)  # is_private - флаг для заданий, к которым нельзя обратиться через api
    as_gia = Column(Boolean, default=False)
    # as_gia - флаг для заданий с решуегэ (система начисления баллов "все или ничего")


class Answers(SqlAlchemyBase):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ask_id = Column(Integer, ForeignKey("testasks.id"))
    ask = orm.relationship('TestAsks')
    ans_text = Column(String)
    is_cor = Column(Boolean)
