import datetime as dt
from . import db


class PhoneToken(db.Model):
    """Represent a pending phone number validation."""

    __tablename__ = 'phone_tokens'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    expiration = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    phone_number = db.Column(db.String(20), nullable=False)
    validation_code = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        if not self.id:
            return '<PhoneToken %s>' % self.phone_number
        else:
            return '<PhoneToken %d: %s>' % (self.id, self.phone_number)