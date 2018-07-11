from datetime import datetime
from cliqcard_server.models import db


group_members_phones_table = db.Table('groups_members__phones', db.Model.metadata,
    db.Column('group_member_id', db.Integer, db.ForeignKey('group_members.id')),
    db.Column('phone_id', db.Integer, db.ForeignKey('phones.id'))
)

group_members_emails_table = db.Table('groups_members__emails', db.Model.metadata,
    db.Column('group_member_id', db.Integer, db.ForeignKey('group_members.id')),
    db.Column('email_id', db.Integer, db.ForeignKey('emails.id'))
)

class GroupMember(db.Model):
    """
    Represents a single user's membership to a contact group.
    """

    __tablename__ = 'group_members'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'))

    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', backref=db.backref('group_members'))
    group = db.relationship('Group', backref=db.backref('group_members'))

    phones = db.relationship("Phone", secondary=group_members_phones_table, backref='group_members')
    emails = db.relationship("Email", secondary=group_members_emails_table, backref='group_members')

    def __repr__(self):
        return '<GroupMember user:%d group%d>' % (self.user_id, self.group_id)