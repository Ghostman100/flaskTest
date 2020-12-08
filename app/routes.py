from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

from app import db, login_manager, app
from app.models import User, Poll, Question, PossibleAnswer, Answer
from app.forms import LoginForm, RegisterForm, PollForm, PollAnswerForm

POLL_TYPES = {
    'poll': 'Опрос',
    'vote': 'Голосование'
}
QUESTIONS_TYPES = {
    'text': 'Свободный ответ',
    'variants': 'Варианты ответа',
}


@app.context_processor
def inject_constants():
    return dict(poll_types=POLL_TYPES, questions_types=QUESTIONS_TYPES)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    polls = Poll.query.all()
    return render_template('index.html', polls=polls)


@app.route('/poll/<poll_id>', methods=['POST', 'GET'])
def view_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    return render_template('poll_info.html', poll=poll)


@app.route('/poll/create', methods=['POST', 'GET'])
@login_required
def create():
    users = [(user.id, user.login) for user in User.query.all()]
    form = PollForm()
    form.access_participation.choices = users
    form.access_results.choices = users
    if form.validate_on_submit():
        new_poll = Poll(title=form.title.data, kind='poll', repeat_type=form.repeat_type.data,
                        creator=current_user)
        for participant_id in form.access_participation.data:
            new_poll.access_participation.append(User.query.get(int(participant_id)))

        for user_id in form.access_results.data:
            new_poll.access_results.append(User.query.get(int(user_id)))

        for question in form.questions:
            if question.question.data:
                if question.kind.data == 'variants':
                    new_question = Question(type='variants', question=question.question.data,
                                            multiple_answers=question.multiple_answers.data)
                    for option in question.options:
                        if option.data:
                            possible_answer = PossibleAnswer(option=option.data, question=new_question)
                            new_question.possible_answers.append(possible_answer)
                else:
                    new_question = Question(type='text', question=question.question.data)
                new_poll.questions.append(new_question)

        db.session.add(new_poll)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        form.questions.append_entry()  # add 5 form
        form.questions.append_entry()
        form.questions.append_entry()
        form.questions.append_entry()
        form.questions.append_entry()
        return render_template('createPoll.html', form=form)


@app.route('/vote/create', methods=['POST', 'GET'])
@login_required
def create_vote():
    users = [(user.id, user.login) for user in User.query.all()]
    form = PollForm()
    form.access_participation.choices = users
    form.access_results.choices = users
    if form.validate_on_submit():
        new_poll = Poll(title=form.title.data, kind='vote', repeat_type=form.repeat_type.data,
                        creator=current_user)
        for participant_id in form.access_participation:
            new_poll.access_participation.append(User.query.get(int(participant_id.data)))

        for user_id in form.access_results:
            new_poll.access_results.append(User.query.get(int(user_id.data)))

        question = form.vote_questions[0]
        if question.question.data:
            new_question = Question(type='variants', question=question.question.data,
                                    multiple_answers=question.multiple_answers.data)
            for option in question.options:
                if option.data:
                    possible_answer = PossibleAnswer(option=option.data, question=new_question)
                    new_question.possible_answers.append(possible_answer)
            new_poll.questions.append(new_question)
            db.session.add(new_poll)
            db.session.commit()
            return redirect(url_for('index'))
    if len(form.questions) == 0:
        form.vote_questions.append_entry()
    return render_template('createVote.html', form=form)


@app.route('/poll/<poll_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_poll(poll_id):
    users = [(user.id, user.login) for user in User.query.all()]
    poll = Poll.query.get_or_404(poll_id)

    if poll.creator != current_user:
        return redirect(url_for('view_poll', poll_id=poll.id))

    form = PollForm()
    form.access_participation.choices = users
    form.access_results.choices = users

    if form.validate_on_submit():
        poll.title = form.title.data
        poll.repeat_type = form.repeat_type.data
        if form.access_participation:
            print(form.access_participation.data)
            for participant_id in form.access_participation.data:
                poll.access_participation.clear()
                poll.access_participation.append(User.query.get(int(participant_id)))
        else:
            poll.access_participation.clear()

        if form.access_results:
            for user_id in form.access_results.data:
                print('asdas', User.query.get(int(user_id)))
                poll.access_results.clear()
                poll.access_results.append(User.query.get(int(user_id)))
        else:
            poll.access_results.clear()

        for i in range(len(poll.questions)):
            question = poll.questions[i]
            form_question = form.questions[i]
            question.question = form_question.question.data
            question.multiple_answers = form_question.multiple_answers.data
            if question.type == 'variants':
                if form_question.kind.data == 'variants':
                    for j in range(len(question.possible_answers)):
                        question.possible_answers[j].option = form_question.options[j].data
                else:
                    question.type = 'text'
                    question.possible_answers.clear()
            else:
                if form_question.kind.data == 'variants':
                    for option in form_question.options:
                        question.type = 'variants'
                        possible_answer = PossibleAnswer(option=option.data, question=question)
                        question.possible_answers.append(possible_answer)

        db.session.add(poll)
        db.session.commit()
        return redirect(url_for('view_poll', poll_id=poll.id))

    # data = {
    #
    #     'repeat_type': poll.repeat_type,
    #     'access_participation': [str(user.id) for user in poll.access_participation],
    #     'access_results': [str(user.id) for user in poll.access_results],
    # }
    form.title.data = poll.title
    form.repeat_type.data = poll.repeat_type
    form.access_participation.data = [str(user.id) for user in poll.access_participation]
    form.title.access_results = [str(user.id) for user in poll.access_results]

    for question in poll.questions:
        if question.type == 'variants':

            form.questions.append_entry({
                'kind': question.type,
                'question': question.question,
                'multiple_answers': question.multiple_answers,
                'options': [option.option for option in question.possible_answers]
            })
        else:
            form.questions.append_entry({
                'kind': question.type,
                'multiple_answers': question.multiple_answers,
                'question': question.question
            })

    return render_template('edit_poll.html', form=form)


@app.route('/poll/<poll_id>/delete')
def delete_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)

    if poll.creator != current_user:
        return redirect(url_for('view_poll', poll_id=poll.id))

    db.session.delete(poll)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/poll/<poll_id>/answer', methods=['GET', 'POST'])
@login_required
def answer(poll_id):
    poll = Poll.query.get_or_404(poll_id)

    if current_user != poll.creator:
        if current_user not in poll.access_participation:
            if current_user in poll.access_results:
                return redirect(url_for('results', poll_id=poll_id))
            else:
                return redirect(url_for('view_poll', poll_id=poll_id))

    if poll.participation_in(current_user) and poll.repeat_type == 'false':
        if current_user in poll.access_results or current_user == poll.creator:
            return redirect(url_for('results', poll_id=poll_id))
        else:
            return redirect(url_for('my_answers', poll_id=poll_id))

    form = PollAnswerForm()

    if request.method == 'POST':
        for form_answer in form.answers:
            question = Question.query.get(form_answer.question_id.data)
            new_answer = Answer(user=current_user, question=question)
            if question.type == 'variants':
                if question.multiple_answers:
                    for option in form_answer.multi_selected_option.data:
                        new_answer.selected_option.append(PossibleAnswer.query.get(option))
                else:
                    new_answer.selected_option.append(PossibleAnswer.query.get(form_answer.selected_option.data))
            else:
                new_answer.answer = form_answer.text_answer.data
            db.session.add(new_answer)
        db.session.commit()
        return redirect(url_for('index'))

    for question in poll.questions:
        answer_form = form.answers.append_entry()
        answer_form.question_id.data = question.id
        if question.type == 'variants':
            choices = []
            for option in question.possible_answers:
                choices.append((option.id, option.option))
            if question.multiple_answers:
                answer_form.kind.data = 'multiSelect'
                answer_form.multi_selected_option.choices = choices
            else:
                answer_form.kind.data = 'select'
                answer_form.selected_option.choices = choices
        else:
            answer_form.kind.data = 'text'
        answer_form.label = question.question
    return render_template('new_answer.html', form=form)


@app.route('/poll/<poll_id>/results')
@login_required
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if current_user != poll.creator:
        if current_user not in poll.access_results:
            return redirect(url_for('view_poll', poll_id=poll_id))

    all_answers = {}
    for user in (set(poll.access_participation) | {poll.creator}):
        user_answers = {}
        for question in poll.questions:
            question_answers = {'type': question.type, 'answers': []}
            if Answer.query.filter_by(question=question, user=user).all():
                for answer in Answer.query.filter_by(question=question, user=user):
                    if question.type == 'variants':
                        question_answers['answers'].append([option.option for option in answer.selected_option])
                    else:
                        question_answers['answers'].append(answer.answer)
                user_answers[question.question] = question_answers
        if user_answers:
            all_answers[user.login] = user_answers

    return render_template('results.html', poll=poll, answers=all_answers)


@app.route('/poll/<poll_id>/upload')
def upload_results(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if current_user != poll.creator:
        if current_user not in poll.access_results:
            return redirect(url_for('view_poll', poll_id=poll_id))

    all_answers = {}
    for user in (set(poll.access_participation) | {current_user}):
        user_answers = {}
        for question in poll.questions:
            question_answers = {'type': question.type, 'answers': []}
            if Answer.query.filter_by(question=question, user=user).all():
                for answer in Answer.query.filter_by(question=question, user=user):
                    if question.type == 'variants':
                        question_answers['answers'].append([option.option for option in answer.selected_option])
                    else:
                        question_answers['answers'].append(answer.answer)
                user_answers[question.question] = question_answers
        if user_answers:
            all_answers[user.login] = user_answers
    return jsonify(all_answers)


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


@app.route('/profile/polls')
@login_required
def own_polls():
    polls = current_user.polls
    return render_template('polls.html', polls=polls)


@app.route('/profile/polls/<poll_id>/answers')
@login_required
def my_answers(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    all_answers = {}
    user_answers = {}
    for question in poll.questions:
        question_answers = {'type': question.type, 'answers': []}
        for answer in Answer.query.filter_by(question=question, user=current_user):
            if question.type == 'variants':
                question_answers['answers'].append([option.option for option in answer.selected_option])
            else:
                question_answers['answers'].append(answer.answer)
        user_answers[question.question] = question_answers
    all_answers[current_user.login] = user_answers

    return render_template('results.html', poll=poll, answers=all_answers, my=True)


@app.route('/profile/available')
def available_polls():
    available_polls_query = current_user.participation_in_poll
    own_polls_query = current_user.polls
    polls = set(own_polls_query) | set(available_polls_query)
    return render_template('polls.html', polls=polls)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
