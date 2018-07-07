from datetime import datetime
from cliqcard_server.models import db


class GroupMember(db.Model):
    """
    Represents a single user's membership to a contact group.
    """

    __tablename__ = 'group_members'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)

    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('group_members'))
    group = db.relationship('Group', backref=db.backref('group_members'))

    shares_personal_card = db.Column(db.Boolean, default=True)
    shares_work_card = db.Column(db.Boolean, default=True)

    shares_home_phone = db.Column(db.Boolean, default=True)
    shares_cell_phone = db.Column(db.Boolean, default=True)
    shares_office_phone = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<GroupMember user:%d group%d>' % (self.user_id, self.group_id)