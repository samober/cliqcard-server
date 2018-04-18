from datetime import datetime
from cliqcard_server.models import db


class GroupJoinCode(db.Model):
    """
    Represent a temporary code that users can use to join a group.
    """

    __tablename__ = 'group_join_codes'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expiration = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    code = db.Column(db.String(12), nullable=False, unique=False)

    group = db.relationship('Group')

    def __repr__(self):
        return '<GroupJoinCode group: %d, code: %s>' % (self.group_id, self.code)