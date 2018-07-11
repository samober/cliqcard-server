from datetime import datetime
from . import db


class Phone(db.Model):
    """
    Represents a phone number of a user
    """

    __tablename__ = 'phones'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    type = db.Column(db.String(16), nullable=False)
    number = db.Column(db.String(16), nullable=False)
    extension = db.Column(db.String(8))

    is_primary = db.Column(db.Boolean, nullable=False, default=False)