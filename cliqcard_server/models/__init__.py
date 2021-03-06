from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .phone_token import PhoneToken
from .registration_token import RegistrationToken
from .address import Address
from .group import Group
from .group_member import GroupMember
from .group_join_code import GroupJoinCode
from .oauth_client import OAuthClient
from .oauth_token import OAuthToken
from .profile_picture import ProfilePicture
from .group_picture import GroupPicture
from .phone import Phone
from .email import Email