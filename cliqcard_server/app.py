from flask import Flask, jsonify
from flask_migrate import Migrate
from .config import app_config
from .errors import APIError
from .views import account, oauth, contacts, groups, users, phones, emails
from .extensions import bcrypt, setup_oauth_server
from .models import db


def create_app(config_name):
    # create the application instance
    app = Flask(__name__)
    # setup configuration from environment variable
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_envvar('CLIQCARD_SERVER_SETTINGS', silent=True)
    app.secret_key = '\x84\xeaE#\xa79\x9dN\xa1y:\x03\x1b\xe9b\x8c\x91\x83\x00\x0c\x9dKZ\xd9'
    app.url_map.strict_slashes = False

    # setup database
    db.init_app(app)

    # setup migrations
    migrate = Migrate(app, db)

    # setup extensions
    bcrypt.init_app(app)
    oauth_server = setup_oauth_server(app)

    # error handlers

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # oauth endpoints
    @app.route('/oauth/token', methods=['POST'])
    def issue_token():
        return oauth_server.create_token_response()

    app.register_blueprint(oauth)
    app.register_blueprint(account)
    app.register_blueprint(users)
    app.register_blueprint(contacts)
    app.register_blueprint(groups)
    app.register_blueprint(phones)
    app.register_blueprint(emails)

    return app


