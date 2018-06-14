import time
from cliqcard_server.models import db


class RegistrationToken(db.Model):
    """
    Represents a token used by the client after successfully verifying a new phone number
    to make a new user account.
    """

    __tablename__ = 'registration_tokens'

    id = db.Column(db.Integer, primary_key=True)
    issued_at = db.Column(db.Integer, nullable=False, default=int(time.time()))
    expires_in = db.Column(db.Integer, nullable=False, default=3600)
    token = db.Column(db.String(256), nullable=False, unique=True)
    phone_number = db.Column(db.String(80), nullable=False, unique=True)

    def __repr__(self):
        return '<RegistrationToken %s>' % self.phone_number

    def is_expired(self):
        return int(time.time()) > self.issued_at + self.expires_in