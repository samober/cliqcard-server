from datetime import datetime
from cliqcard_server.models import db


class Address(db.Model):
    """
    Represents a street address that can be added to a card.
    """

    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    street1 = db.Column(db.String(80))
    street2 = db.Column(db.String(80))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    zip = db.Column(db.String(12))
    country = db.Column(db.String(80))

    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)

    def __repr__(self):
        return '<Address card: %d>' % self.card_id