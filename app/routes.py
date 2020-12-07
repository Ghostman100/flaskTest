from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager, app
from app.models import User, Poll, Question, PossibleAnswer
from app.forms import LoginForm, RegisterForm, NewPollForm


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    polls = Poll.query.all()
    return render_template('index.html', polls=polls)


@app.route('/poll/create', methods=['POST', 'GET'])
def create():
    users = [(user.id, user.login) for user in User.query.all()]
    form = NewPollForm()
    form.access_participation.choices = users
    form.access_results.choices = users
    if form.validate_on_submit():
        new_poll = Poll(title=form.title.data, kind=form.kind.data, repeat_type=form.repeat_type.data, creator=current_user)
        for participant_id in form.access_participation:
            new_poll.access_participation.append(User.query.get(int(participant_id.data)))

        for user_id in form.access_results:
            new_poll.access_results.append(User.query.get(int(user_id.data)))

        for question in form.questions:
            if question.kind.data == 'variants':
                new_question = Question(type='variants', question=question.question.data)
                for option in question.options:
                    possible_answer = PossibleAnswer(option=option.data, question=new_question)
                    new_question.possible_answers.append(possible_answer)
            else:
                new_question = Question(type='text', question=question.question.data)
            new_poll.questions.append(new_question)
        db.session.add(new_poll)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('createPoll.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        error = 'Неверный логин или пароль'
    return render_template('login.html', form=form, error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()
    print(form.errors.items())
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            flash('Пароли не совпадают')
        else:
            hash_pwd = generate_password_hash(form.password1.data)
            if User.query.filter_by(login=form.login.data.lower()).first():
                flash('Пользователь с таким именем уже существует')
                return render_template('register.html')
            new_user = User(login=form.login.data, password_hash=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

