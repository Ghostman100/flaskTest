from flask_restful import Resource, reqparse

from app.models import Poll, Answer, User, PossibleAnswer
from app.models import db


class PollResource(Resource):
    def get(self, poll_id=0):
        poll = Poll.query.get_or_404(poll_id)
        questions = []
        for question in poll.questions:
            question_dict = {
                'id': question.id,
                'type': question.type,
                'question': question.question,
            }
            if question.type == 'variants':
                question_dict['multiple_answers'] = question.multiple_answers
                question_dict['options'] = [{'id': option.id, 'value': option.option} for option in
                                            question.possible_answers]
            questions.append({'questions': question_dict})
        return questions


class AnswerResource(Resource):

    def post(self, poll_id):
        poll = Poll.query.get_or_404(poll_id)
        parser = reqparse.RequestParser()
        parser.add_argument("user_login", type=str)
        parser.add_argument("answers", type=dict, action="append")
        answers = parser.parse_args()
        user = User.query.filter_by(login=answers.user_login).first()
        print(answers, user)
        for question in poll.questions:
            id_in_json = False
            for answer in answers.answers:
                if question.id == answer['question_id']:
                    id_in_json = True
                    new_answer = Answer(user=user, question=question)
                    if question.type == 'variants':
                        if question.multiple_answers:
                            for option in answer['multiple_answers']:
                                new_answer.selected_option.append(PossibleAnswer.query.get_or_404(option))
                        else:
                            new_answer.selected_option.append(PossibleAnswer.query.get(answer['select_answer']))
                    else:
                        new_answer.answer = answer['text_answer']
                    db.session.add(new_answer)
                    break
            if not id_in_json:
                return f"question {question.id} does not exist", 400
        db.session.commit()
        return 'OK', 200

