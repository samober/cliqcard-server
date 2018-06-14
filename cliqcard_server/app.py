from flask import Flask, jsonify
from flask_migrate import Migrate
from .config import app_config


def create_app(config_name):
    # create the application instance
    app = Flask(__name__)
    # setup configuration from environment variable
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_envvar('CLIQCARD_SERVER_SETTINGS', silent=True)
    app.secret_key = '\x84\xeaE#\xa79\x9dN\xa1y:\x03\x1b\xe9b\x8c\x91\x83\x00\x0c\x9dKZ\xd9'

    # setup database
    from cliqcard_server.models import db
    db.init_app(app)

    # setup migrations
    migrate = Migrate(app, db)

    # setup bcrypt
    from cliqcard_server.extensions import bcrypt
    bcrypt.init_app(app)

    # setup oauth
    from cliqcard_server.extensions import setup_oauth_server
    oauth_server = setup_oauth_server(app)



    # error handlers

    @app.errorhandler(401)
    def not_authorized(e):
        response = jsonify({
            'message': 'You are not authorized to access this.'
        })
        response.status_code = 401
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        response = jsonify({
            'message': 'The resource you are trying to reach does not exist.'
        })
        response.status_code = 404
        return response

    # set up auth endpoints
    from cliqcard_server.views.auth import VerifyPhoneView, GetRegistrationTokenView, RefreshAccessTokenView
    app.add_url_rule('/verify_phone', view_func=VerifyPhoneView.as_view('verify_phone'), methods=['POST'])
    # app.add_url_rule('/register', view_func=GetRegistrationTokenView.as_view('register'), methods=['POST'])

    # oauth endpoints
    @app.route('/oauth/token', methods=['POST'])
    def issue_token():
        return oauth_server.create_token_response()

    # setup account endpoints
    from cliqcard_server.views.account import AccountView
    app.add_url_rule('/account', view_func=AccountView.as_view('account'), methods=['GET', 'POST', 'PUT', 'DELETE'])

    # set up user endpoints
    from cliqcard_server.views.user import UserAPI
    user_view = UserAPI.as_view('user_api')
    app.add_url_rule('/users', defaults={'user_id': None}, view_func=user_view, methods=['GET'])
    app.add_url_rule('/users/<int:user_id>', view_func=user_view, methods=['GET'])

    from cliqcard_server.views import cards
    app.register_blueprint(cards.bp)

    from cliqcard_server.views import contacts
    app.register_blueprint(contacts.bp)

    from cliqcard_server.views import groups
    app.register_blueprint(groups.bp)

    return app


