from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restful import Api

from app.api_resource import PollResource, AnswerResource
from app.models import db


app = Flask(__name__)
# with app.app_context():
app.config.from_object('app.config')
login_manager = LoginManager(app)
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

api.add_resource(PollResource, '/api/poll/<int:poll_id>')
api.add_resource(AnswerResource, '/api/poll/<int:poll_id>/answer')


from app import routes, models
