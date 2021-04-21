import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Set appliction config
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///rest.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['JSON_SORT_KEYS'] = False #Prevents sorting after using jsonify 
    db.init_app(app)

    # Import Blueprint and Models
    from app.api import api_blueprint
    from app.models import restaurant

    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Creates database and tables if they not exist
    with app.app_context():
        db.create_all()

    return app
