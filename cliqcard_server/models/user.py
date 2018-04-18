import datetime as dt
from . import db
from .card import Card

from sqlalchemy.ext.associationproxy import association_proxy


class User(db.Model):
    """Represents the users table in the database."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

    email = db.Column(db.String(120), unique=True)

    refresh_token = db.relationship('RefreshToken', backref='user', lazy=True, uselist=False)

    cards = db.relationship('Card', backref='user', lazy=True)

    groups = association_proxy('group_members', 'group')
    managed_groups = db.relationship('Group', backref='admin', lazy=True)

    def __repr__(self):
        return '<User %d: %s %s>' % (self.id, self.first_name, self.last_name)

    @property
    def personal_card(self):
        for card in self.cards:
            if card.label == Card.CardLabel.personal:
                return card
        return None

    @personal_card.setter
    def personal_card(self, value):
        # delete old card
        for card in self.cards:
            if card.label == Card.CardLabel.personal:
                db.session.delete(card)
        value.user = self
        value.label = Card.CardLabel.personal
        db.session.add(value)
        db.session.commit()

    @property
    def work_card(self):
        for card in self.cards:
            if card.label == Card.CardLabel.work:
                return card
        return None

    @work_card.setter
    def work_card(self, value):
        # delete old card
        for card in self.cards:
            if card.label == Card.CardLabel.work:
                db.session.delete(card)
        value.user = self
        value.label = Card.CardLabel.work
        db.session.add(value)
        db.session.commit()