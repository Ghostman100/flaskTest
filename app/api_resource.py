from flask_restful import Resource, reqparse
from app.models import Poll


class PollResource(Resource):
    def get(self, poll_id=0):
        poll = Poll.query.get_or_404(poll_id)
        questions = []
        for question in poll.questions:
            question_dict = {
                'id': poll.id,
                'type': question.type,
                'question': question.question,
            }
            if question.type == 'variants':
                question_dict['multiple_answers'] = question.multiple_answers,
                question_dict['options'] = [{'id': option.id, 'value': option.option} for option in
                                            question.possible_answers]
            questions.append({'questions': question_dict})
        return questions

    def answer(self, poll_id=0):
        poll = Poll.query.get_or_404(poll_id)
        parser = reqparse.RequestParser()
        parser.add_argument("answers", type=dict, action="append")
        answers = parser.parse_args()

        pass


a = {'answers': [{'id': 1,
                  'text_answer': 'asda',
                  'select_answer': 21,
                  'multiple_answers': [12, 32]
                  }]}
