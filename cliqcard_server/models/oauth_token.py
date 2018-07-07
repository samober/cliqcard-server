from cliqcard_server.models import db
from authlib.flask.oauth2.sqla import OAuth2TokenMixin
import time


class OAuthToken(db.Model, OAuth2TokenMixin):
    """
    Represents an access token used to authorize users with the API.
    """

    __tablename__ = "oauthtokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_access_token_expired(self):
        return int(time.time()) > self.issued_at + self.expires_in