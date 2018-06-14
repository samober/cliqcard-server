import time
from cliqcard_server.models import db


class GroupJoinCode(db.Model):
    """
    Represent a temporary code that users can use to join a group.
    """

    __tablename__ = 'group_join_codes'

    id = db.Column(db.Integer, primary_key=True)
    issued_at = db.Column(db.Integer, nullable=False, default=int(time.time()))
    expires_in = db.Column(db.Integer, nullable=False, default=1209600)

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    code = db.Column(db.String(12), nullable=False, unique=False)

    group = db.relationship('Group')

    def __repr__(self):
        return '<GroupJoinCode group: %d, code: %s>' % (self.group_id, self.code)

    def is_expired(self):
        return int(time.time()) > self.issued_at + self.expires_in