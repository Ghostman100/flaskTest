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
    polls = relationship('Poll', back_populates='creator')
    answers = relationship('Answer', back_populates='user', lazy='joined')


class Poll(db.Model):
    __tablename__ = 'poll'

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    repeat_type = db.Column(db.Boolean(), default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = relationship('User', back_populates='polls')
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    access_participation = relationship(
        'User',
        secondary=user_poll_participate_access_table,
        backref='participation_in_poll')
    access_results = relationship(
        'User',
        secondary=user_poll_results_access_table,
        backref='available_for_viewing_results')
    questions = relationship('Question', back_populates='poll', cascade="all, delete-orphan")

    def participation_in(self, user):
        return bool(Answer.query.filter_by(user=user, question=self.questions[0]).first())


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(), nullable=False)
    question = db.Column(db.String(), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    poll = relationship('Poll', back_populates='questions')
    multiple_answers = db.Column(db.Boolean, default=False)
    answers = relationship('Answer', back_populates='question', cascade="all, delete-orphan")
    possible_answers = relationship('PossibleAnswer', back_populates='question', cascade="all, delete-orphan")


class PossibleAnswer(db.Model):
    __tablename__ = 'possible_answer'

    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(), nullable=False)
    question_id = db.Column(db.Integer(), db.ForeignKey('question.id'))
    question = relationship('Question', back_populates='possible_answers')


answers_selected_option_table = db.Table('selected_option', db.Model.metadata,
                                         db.Column('answer_id', db.Integer, db.ForeignKey('answer.id')),
                                         db.Column('possible_answer_id', db.Integer,
                                                   db.ForeignKey('possible_answer.id'))
                                         )


class Answer(db.Model):
    __tablename__ = 'answer'

    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String())
    # possible_answer_id = db.Column(db.Integer, db.ForeignKey('possible_answer.id'))
    # selected_option = relationship('PossibleAnswer', back_populates='answers')
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = relationship('Question', back_populates='answers')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='answers')
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    selected_option = relationship(
        'PossibleAnswer',
        secondary=answers_selected_option_table,
        backref='answers')
