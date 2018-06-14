import time
from . import db


class PhoneToken(db.Model):
    """Represent a pending phone number validation."""

    __tablename__ = 'phone_tokens'

    id = db.Column(db.Integer, primary_key=True)
    issued_at = db.Column(db.Integer, nullable=False, default=int(time.time()))
    expires_in = db.Column(db.Integer, nullable=False, default=3600)
    phone_number = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        if not self.id:
            return '<PhoneToken %s>' % self.phone_number
        else:
            return '<PhoneToken %d: %s>' % (self.id, self.phone_number)

    def is_expired(self):
        return int(time.time()) > self.issued_at + self.expires_in