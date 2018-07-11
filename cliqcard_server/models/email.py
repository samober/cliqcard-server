from datetime import datetime
from . import db


class Email(db.Model):
    """
    Represents a user's email address
    """

    __tablename__ = 'emails'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    type = db.Column(db.String(16), nullable=False)
    address = db.Column(db.String(64), nullable=False)

    is_primary = db.Column(db.Boolean, nullable=False, default=False)