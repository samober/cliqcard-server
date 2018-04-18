from datetime import datetime
from cliqcard_server.models import db

from sqlalchemy import func
from sqlalchemy.ext.associationproxy import association_proxy


class Group(db.Model):
    """
    Represents a contact group.
    """

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    name = db.Column(db.String(140), nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    members = association_proxy('group_members', 'user')

    def __repr__(self):
        return '<Group %s>' % self.name

    @property
    def member_count(self):
        from cliqcard_server.models import GroupMember
        return db.session.query(func.count(GroupMember.user_id)).filter_by(group_id=self.id).scalar()