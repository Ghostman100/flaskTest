from flask import Flask, current_app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api

from app.api_resource import PollResource


app = Flask(__name__)
# with app.app_context():
app.config.from_object('app.config')
login_manager = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

api.add_resource(PollResource, '/api/poll/<int:id>')

from app import routes, models
