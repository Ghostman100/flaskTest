from wtforms import *
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=4, max=100)])


class RegisterForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password1 = PasswordField('password1', validators=[DataRequired(), Length(min=4, max=100)])
    password2 = PasswordField('password2', validators=[DataRequired(), Length(min=4, max=100)])


class AnswerForm(FlaskForm):
    text_answer = TextAreaField('Ответ', render_kw={'class': 'form-group'})
    selected_option = SelectField('Вариант', render_kw={'class': "custom-select"}, choices=[], coerce=int)
    multi_selected_option = SelectMultipleField('Вариант', render_kw={'class': 'custom-select'}, choices=[], coerce=int)
    kind = HiddenField()
    question_id = HiddenField()


class PollAnswerForm(FlaskForm):
    answers = FieldList(FormField(AnswerForm))


class VoteQuestionForm(FlaskForm):
    question = StringField('Вопрос', render_kw={'class': 'form-group'})
    multiple_answers = BooleanField('Множественное голосование')
    options = FieldList(StringField('Вариант', render_kw={'class': 'form-group'}), min_entries=5)


class QuestionForm(FlaskForm):
    question = StringField('Вопрос', render_kw={'class': 'form-group'})
    kind = SelectField('Тип вопроса', choices=[('text', 'Свободный ответ'), ('variants', 'Варианты ответа')],
                       render_kw={'class': "custom-select"})
    multiple_answers = BooleanField('Множественное голосование')
    options = FieldList(StringField('Вариант', render_kw={'class': 'form-group'}), min_entries=5)


class PollForm(FlaskForm):
    questions = FieldList(FormField(QuestionForm))
    vote_questions = FieldList(FormField(VoteQuestionForm))
    title = StringField('title', validators=[DataRequired()], render_kw={'class': 'form-group'})
    # kind = SelectField('kind', choices=[('poll', 'Опрос'), ('vote', 'Голосование')])
    repeat_type = BooleanField('repeat_type')
    access_participation = SelectMultipleField('Кто может участвовать', coerce=int)
    access_results = SelectMultipleField('Кто может видеть результаты', coerce=int)
