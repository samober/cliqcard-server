from datetime import datetime
from . import db


class GroupPicture(db.Model):
    """
    Represents a group's pictures in different sizes
    """

    __tablename__ = 'group_pictures'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    original = db.Column(db.String(128), nullable=False)
    thumb_big = db.Column(db.String(128), nullable=False)     # 128x128
    thumb_normal = db.Column(db.String(128), nullable=False)  # 84x84
    thumb_small = db.Column(db.String(128), nullable=False)   # 58x58
    thumb_mini = db.Column(db.String(128), nullable=False)    # 32x32

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'))