from datetime import datetime
from cliqcard_server.models import db

from sqlalchemy import func, exists, and_
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

    picture = db.relationship('GroupPicture', backref='group', uselist=False)

    members = association_proxy('group_members', 'user')

    def __repr__(self):
        return '<Group %s>' % self.name

    @property
    def member_count(self):
        from cliqcard_server.models import GroupMember
        return db.session.query(func.count(GroupMember.user_id)).filter_by(group_id=self.id).scalar()

    def is_admin(self, user):
        from cliqcard_server.models import GroupMember
        return db.session.query(exists().where(and_(GroupMember.group_id==self.id, GroupMember.user_id==user.id, GroupMember.is_admin==True))).scalar()