from datetime import datetime
import secrets
from cliqcard_server.models import db


class RefreshToken(db.Model):
    """
    Represents a refresh token used for requesting new access tokens.
    """

    __tablename__ = 'refresh_tokens'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    token = db.Column(db.String(256), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<RefreshToken %d>' % self.user_id

    @staticmethod
    def generate_random_token():
        return secrets.token_urlsafe(128)