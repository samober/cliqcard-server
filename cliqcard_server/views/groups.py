import datetime
import random
import string
from flask import abort, jsonify, request, Blueprint
from cliqcard_server.serializers import serialize_group, serialize_user, serialize_card, serialize_group_member
from cliqcard_server.utils import require_oauth, current_token
from cliqcard_server.models import db, Group, GroupMember, GroupJoinCode


bp = Blueprint('groups', __name__, url_prefix='/groups')


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/<int:group_id>', methods=['GET', 'PUT'])
@require_oauth(None)
def index(group_id=None):
    if request.method == 'GET':
        if not group_id:
            # get all the groups that the user is currently a member of
            groups = list(current_token.user.groups)
            return jsonify(serialize_group(groups))
        else:
            # get the specific group if the user is a member
            group = Group.query.get(group_id)
            if not group:
                abort(404)

            # find the group member relationship between this group and user
            group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
            if not group_member:
                abort(401)

            return jsonify({
                'group': serialize_group(group),
                'sharing': serialize_group_member(group_member)
            })
    elif request.method == 'POST':
        name = request.json['name']
        share_personal_card = request.json['share_personal_card']
        share_work_card = request.json['share_work_card']
        share_home_phone = request.json.get('share_home_phone', True)
        share_cell_phone = request.json.get('share_cell_phone', True)
        share_office_phone = request.json.get('share_office_phone', True)

        # create the group
        group = Group(name=name, admin_id=current_token.user.id)
        db.session.add(group)
        db.session.commit()

        # create a group member for the current user
        group_member = GroupMember(
            user_id=current_token.user.id,
            group_id=group.id,
            shares_personal_card=share_personal_card,
            shares_work_card=share_work_card,
            shares_home_phone=share_home_phone,
            shares_cell_phone=share_cell_phone,
            shares_office_phone=share_office_phone
        )
        db.session.add(group_member)
        db.session.commit()

        return jsonify(serialize_group(group))
    elif request.method == 'PUT':
        group = Group.query.get(group_id)
        if not group:
            abort(404)

        # find the group member relationship between this group and user
        group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
        if not group_member:
            abort(401)

        # change sharing settings
        group_member.shares_personal_card = request.json.get('share_personal_card', group_member.shares_personal_card)
        group_member.shares_work_card = request.json.get('share_work_card', group_member.shares_work_card)
        group_member.shares_home_phone = request.json.get('share_home_phone', group_member.shares_home_phone)
        group_member.shares_cell_phone = request.json.get('share_cell_phone', group_member.shares_cell_phone)
        group_member.shares_office_phone = request.json.get('share_office_phone', group_member.shares_office_phone)

        # if this user is the admin they can change details about the group
        if group.admin_id == current_token.user.id:
            group.name = request.json.get('name', group.name)

        # commit changes
        db.session.commit()
        return jsonify({
            'group': serialize_group(group),
            'sharing': serialize_group_member(group_member)
        })


@bp.route('/<int:group_id>/members', methods=['GET'], endpoint='group_members')
@require_oauth(None)
def members(group_id):
    # get the group
    group = Group.query.get(group_id)
    if not group:
        abort(404)

    # check if a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if not group_member:
        abort(401)

    # get all the group members
    group_members = list(group.group_members)
    # remove the current user
    group_members.remove(group_member)

    # serialize
    results = []
    for group_member in group_members:
        obj = serialize_user(group_member.user)
        if group_member.shares_personal_card:
            obj['personal_card'] = serialize_card(group_member.user.personal_card)
            if not group_member.shares_home_phone:
                obj['personal_card']['home_phone'] = None
            if not group_member.shares_cell_phone:
                obj['personal_card']['cell_phone'] = None
        if group_member.shares_work_card:
            obj['work_card'] = serialize_card(group_member.user.work_card)
            if not group_member.shares_office_phone:
                obj['personal_card']['office_phone'] = None
        results.append(obj)

    return jsonify(results)


@bp.route('/<int:group_id>/code', methods=['GET'], endpoint='group_join_code')
@require_oauth(None)
def code(group_id):
    # get the group
    group = Group.query.get(group_id)
    if not group:
        abort(404)

    # check if a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if not group_member:
        abort(401)

    # try to find an existing join code
    join_code = GroupJoinCode.query.filter_by(group_id=group.id).first()

    # check if expired
    if join_code and datetime.datetime.utcnow() > join_code.expiration:
        # code expired - delete it
        db.session.delete(join_code)
        join_code = None

    if not join_code:
        # generate a new code
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        join_code = GroupJoinCode(group_id=group.id, code=code,
                                  expiration=datetime.datetime.utcnow() + datetime.timedelta(days=14))
        db.session.add(join_code)
        db.session.commit()

    return jsonify({
        'group': serialize_group(group),
        'join_code': {
            'code': join_code.code,
            'expiration': join_code.expiration
        }
    })


@bp.route('/join', methods=['POST'], endpoint='join_group')
@require_oauth(None)
def join():
    # get join code
    code = request.json['join_code']

    # grab join settings
    share_personal_card = request.json['share_personal_card']
    share_work_card = request.json['share_work_card']
    share_home_phone = request.json.get('share_home_phone', True)
    share_cell_phone = request.json.get('share_cell_phone', True)
    share_office_phone = request.json.get('share_office_phone', True)

    # get the join code from the database
    join_code = GroupJoinCode.query.filter_by(code=code).first()
    if not join_code or datetime.datetime.utcnow() > join_code.expiration:
        response = jsonify({
            'error': 'Invalid or expired join code.'
        })
        response.status_code = 400
        return response

    # get the group
    group = join_code.group

    # check if already a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if group_member:
        return jsonify({
            'group': serialize_group(group),
            'sharing': serialize_group_member(group_member)
        })

    # create a new group member object
    group_member = GroupMember(
        group_id=group.id,
        user_id=current_token.user.id,
        shares_personal_card=share_personal_card,
        shares_work_card=share_work_card,
        shares_home_phone=share_home_phone,
        shares_cell_phone=share_cell_phone,
        shares_office_phone=share_office_phone
    )
    db.session.add(group_member)
    db.session.commit()

    return jsonify({
        'group': serialize_group(group),
        'sharing': serialize_group_member(group_member)
    })
