from datetime import datetime
import enum
from cliqcard_server.models import db


class Card(db.Model):
    """
    Represents a card that user can share to contact groups.
    """

    class CardLabel(enum.Enum):
        personal = 1
        work = 2

    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    label = db.Column(db.Enum(CardLabel), nullable=False)
    phone1 = db.Column(db.String(20)) # cell phone for personal, office for work
    phone2 = db.Column(db.String(20)) # home phone for personal, none for work
    email = db.Column(db.String(80))
    address = db.relationship('Address', backref='card', uselist=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Card %d>' % self.user_id