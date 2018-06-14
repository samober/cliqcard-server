from authlib.flask.oauth2.sqla import OAuth2ClientMixin
from cliqcard_server.models import db


class OAuthClient(db.Model, OAuth2ClientMixin):
    """
    Represents an authorized OAuth client application using the API.
    """

    __tablename__ = 'oauthclients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')