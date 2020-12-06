from flask_login import UserMixin
from sqlalchemy.orm import relationship
from datetime import datetime
from app import db


user_poll_participate_access_table = db.Table('participate_access', db.Model.metadata,
                                              db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                              db.Column('poll_id', db.Integer, db.ForeignKey('poll.id'))
                                              )

user_poll_results_access_table = db.Table('results_access', db.Model.metadata,
                                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                          db.Column('poll_id', db.Integer, db.ForeignKey('poll.id'))
                                          )


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    polls = relationship('Poll')


class Poll(db.Model):
    __tablename__ = 'poll'

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(), nullable=False)
    repeat_type = db.Column(db.String(), default='no repeat')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = relationship('User')
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    access_participation = relationship(
        'User',
        secondary=user_poll_participate_access_table,
        back_populates='participation_in_poll')
    access_results = relationship(
        'User',
        secondary=user_poll_results_access_table,
        back_populates='available_for_viewing_results')
    questions = relationship('Question')


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(), nullable=False)
    question = db.Column(db.String(), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    poll = relationship('Poll')
    answers = relationship('Answer')
    possible_answers = relationship('PossibleAnswer')


class PossibleAnswer(db.Model):
    __tablename__ = 'possible_answer'

    option = db.Column(db.String(), nullable=False)
    question_id = db.Column(db.Integer(), db.ForeignKey('question.id'))
    question = relationship('Question')


class Answer(db.Model):
    __tablename__ = 'answer'

    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = relationship('Question')
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
