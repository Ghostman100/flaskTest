from wtforms import StringField, PasswordField, FieldList, SelectField, SelectMultipleField, FormField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=4, max=100)])


class RegisterForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password1 = PasswordField('password1', validators=[DataRequired(), Length(min=4, max=100)])
    password2 = PasswordField('password2', validators=[DataRequired(), Length(min=4, max=100)])


class QuestionForm(FlaskForm):
    question = StringField('question', validators=[DataRequired()], render_kw={'class': 'form-group'})
    kind = SelectField('Тип вопроса', choices=[('variants', 'Варианты ответа'), ('text', 'Свободный ответ')],
                       render_kw={'class': "custom-select"})
    options = FieldList(StringField('options', render_kw={'class': 'form-group'}), min_entries=3)


class NewPollForm(FlaskForm):
    questions = FieldList(FormField(QuestionForm), min_entries=2)
    title = StringField('title', validators=[DataRequired()], render_kw={'class': 'form-group'})
    kind = SelectField('kind', choices=[('poll', 'Опрос'), ('vote', 'Голосование')])
    repeat_type = SelectField('repeat_type',
                              choices=[('no repeat', 'Без повторов'),
                                       ('revote', 'Повторное голосование'),
                                       ('multiple voting', 'Множественное голосование')])
    access_participation = SelectMultipleField('Кто может участвовать', coerce=int)
    access_results = SelectMultipleField('Кто может видеть результаты', coerce=int)
