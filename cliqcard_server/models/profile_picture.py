from datetime import datetime
from . import db


class ProfilePicture(db.Model):
    """
    Represents a user's profile pictures in different sizes
    """

    __tablename__ = 'profile_pictures'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    original = db.Column(db.String(128), nullable=False)
    thumb_big = db.Column(db.String(128), nullable=False)     # 128x128
    thumb_normal = db.Column(db.String(128), nullable=False)  # 84x84
    thumb_small = db.Column(db.String(128), nullable=False)   # 58x58
    thumb_mini = db.Column(db.String(128), nullable=False)    # 32x32

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))