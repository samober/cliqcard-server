from flask import request, jsonify, abort
from flask.views import MethodView
from cliqcard_server.models import db, User
from cliqcard_server.utils import require_oauth
from cliqcard_server.serializers import serialize_user


class UserAPI(MethodView):

    @require_oauth(None)
    def get(self, user_id):
        if user_id is None:
            # return all users
            users = User.query.all()
            return jsonify(serialize_user(users))
        else:
            # get specific user by id
            user = User.query.get(user_id)
            if not user:
                abort(404)
            else:
                return jsonify(serialize_user(user))