from flask import jsonify, Blueprint
from cliqcard_server.models import User
from cliqcard_server.utils import require_oauth
from cliqcard_server.serializers import serialize_user
from cliqcard_server.errors import NotFoundError


users = Blueprint('users', __name__, url_prefix='/users')


@users.route('/', methods=['GET'])
@users.route('/<int:user_id>', methods=['GET'])
@require_oauth(None)
def get(user_id=None):
    if user_id is None:
        # return all users
        users = User.query.all()
        return jsonify(serialize_user(users))
    else:
        # get specific user by id
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError()
        else:
            return jsonify(serialize_user(user))