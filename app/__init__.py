from flask import Flask, current_app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
# with app.app_context():
app.config.from_object('app.config')
login_manager = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
