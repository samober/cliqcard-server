import datetime as dt
from . import db

from sqlalchemy.ext.associationproxy import association_proxy


class User(db.Model):
    """Represents the users table in the database."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    profile_picture = db.relationship('ProfilePicture', backref='user', uselist=False)

    phones = db.relationship('Phone', backref='user')
    emails = db.relationship('Email', backref='user')
    addresses = db.relationship('Address', backref='user')

    groups = association_proxy('group_members', 'group')

    def __repr__(self):
        return '<User %d: %s %s>' % (self.id, self.first_name, self.last_name)

    def get_user_id(self):
        return self.id

    @property
    def primary_phone(self):
        from .phone import Phone
        return Phone.query.filter_by(user_id=self.id, is_primary=True).first()

    @property
    def primary_email(self):
        from .email import Email
        return Email.query.filter_by(user_id=self.id, is_primary=True).first()