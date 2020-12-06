from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.forms import LoginForm, RegisterForm
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager, app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/poll/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        pass
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data.lower()).first()
        if user and check_password_hash(user['password_hash'], form.password.data):
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

