import os
from config import config
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


load_dotenv()
db = SQLAlchemy()
ma = Marshmallow()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    ma.init_app(app)

    #Import blueprint and models
    from app.api import api_blueprint
    from app.models import restaurant

    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .utils.restaurant import fill_database_resturants, fill_database_dishes

    with app.app_context():
        db.create_all()
        fill_database_resturants()
        fill_database_dishes()

    return app
