import time
from flask import jsonify, request, Blueprint
from cliqcard_server.serializers import serialize_group, serialize_user, serialize_card, serialize_group_member
from cliqcard_server.utils import require_oauth, current_token, generate_short_code
from cliqcard_server.models import db, Group, GroupMember, GroupJoinCode
from cliqcard_server.errors import UnauthorizedError, NotFoundError, InvalidRequestError


groups = Blueprint('groups', __name__, url_prefix='/groups')


@groups.route('/', methods=['GET', 'POST'])
@groups.route('/<int:group_id>', methods=['GET', 'PUT', 'DELETE'])
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
                raise NotFoundError()

            # find the group member relationship between this group and user
            group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
            if not group_member:
                raise UnauthorizedError()

            return jsonify({
                'group': serialize_group(group),
                'sharing': serialize_group_member(group_member)
            })
    elif request.method == 'POST':
        name = request.json.get('name')
        share_personal_card = request.json.get('share_personal_card')
        share_work_card = request.json.get('share_work_card')
        share_home_phone = request.json.get('share_home_phone', True)
        share_cell_phone = request.json.get('share_cell_phone', True)
        share_office_phone = request.json.get('share_office_phone', True)

        # create the group
        group = Group(name=name)
        db.session.add(group)
        db.session.commit()

        # create a group member for the current user
        group_member = GroupMember(
            user_id=current_token.user.id,
            group_id=group.id,
            is_admin=True,
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
            raise NotFoundError()

        # find the group member relationship between this group and user
        group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
        if not group_member:
            raise UnauthorizedError()

        # change sharing settings
        group_member.shares_personal_card = request.json.get('share_personal_card', group_member.shares_personal_card)
        group_member.shares_work_card = request.json.get('share_work_card', group_member.shares_work_card)
        group_member.shares_home_phone = request.json.get('share_home_phone', group_member.shares_home_phone)
        group_member.shares_cell_phone = request.json.get('share_cell_phone', group_member.shares_cell_phone)
        group_member.shares_office_phone = request.json.get('share_office_phone', group_member.shares_office_phone)

        # if this user is the admin they can change details about the group
        if group_member.is_admin:
            group.name = request.json.get('name', group.name)

        # commit changes
        db.session.commit()
        return jsonify({
            'group': serialize_group(group),
            'sharing': serialize_group_member(group_member)
        })
    elif request.method == 'DELETE':
        group = Group.query.get(group_id)
        if not group:
            raise NotFoundError()

        # find the group member relationship between this group and user
        group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
        if not group_member:
            raise UnauthorizedError()

        # make sure the user is an admin
        if not group_member.is_admin:
            raise UnauthorizedError()

        # delete the group
        db.session.delete(group)
        db.session.commit()

        return ('', 204)


@groups.route('/<int:group_id>/leave', methods=['POST'], endpoint='leave_group')
@require_oauth(None)
def leave(group_id):
    # get the group
    group = Group.query.get(group_id)
    if not group:
        raise NotFoundError()

    # check if a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if not group_member:
        raise UnauthorizedError()

    # check if an admin
    if group_member.is_admin:
        # make sure theyre not the only one left
        admin_count = GroupMember.query.filter_by(group_id=group_id, is_admin=True).count()
        if admin_count == 1:
            # there can't be a group with no admins - he will have to pick someone before he leaves
            raise InvalidRequestError(message='You must pick someone else to take your place as admin of the group'
                                              'before you can leave.')

    # delete the group member entry
    db.session.delete(group_member)
    db.session.commit()

    return ('', 204)



@groups.route('/<int:group_id>/members', methods=['GET'], endpoint='group_members')
@require_oauth(None)
def members(group_id):
    # get the group
    group = Group.query.get(group_id)
    if not group:
        raise NotFoundError()

    # check if a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if not group_member:
        raise UnauthorizedError()

    # get all the group members
    group_members = list(group.group_members)
    # remove the current user
    group_members.remove(group_member)

    # serialize
    results = []
    for group_member in group_members:
        obj = serialize_user(group_member.user)
        if group_member.shares_personal_card:
            personal_card = serialize_card(group_member.user.personal_card)
            if not group_member.shares_home_phone:
                personal_card['home_phone'] = None
            if not group_member.shares_cell_phone:
                personal_card['cell_phone'] = None
            obj['personal_card'] = personal_card
        if group_member.shares_work_card:
            work_card = serialize_card(group_member.user.work_card)
            if not group_member.shares_office_phone:
                work_card['office_phone'] = None
            obj['work_card'] = work_card
        results.append(obj)

    return jsonify(results)


@groups.route('/<int:group_id>/code', methods=['GET'], endpoint='group_join_code')
@require_oauth(None)
def code(group_id):
    # get the group
    group = Group.query.get(group_id)
    if not group:
        raise NotFoundError()

    # check if a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if not group_member:
        raise UnauthorizedError()

    # try to find an existing join code
    join_code = GroupJoinCode.query.filter_by(group_id=group.id).first()

    # check if expired
    if join_code and join_code.is_expired():
        # code expired - delete it
        db.session.delete(join_code)
        join_code = None

    if not join_code:
        # generate a new code
        code = generate_short_code(6)
        join_code = GroupJoinCode(group_id=group.id, code=code, issued_at=int(time.time()), expires_in=43200) # <- 12 hours
        db.session.add(join_code)
        db.session.commit()

    return jsonify({
        'group': serialize_group(group),
        'join_code': {
            'code': join_code.code,
            'expires_in': join_code.expires_in
        }
    })


@groups.route('/join', methods=['POST'], endpoint='join_group')
@require_oauth(None)
def join():
    # get join code
    code = request.json.get('join_code')

    # grab join settings
    share_personal_card = request.json.get('share_personal_card')
    share_work_card = request.json.get('share_work_card')
    share_home_phone = request.json.get('share_home_phone', True)
    share_cell_phone = request.json.get('share_cell_phone', True)
    share_office_phone = request.json.get('share_office_phone', True)

    # get the join code from the database
    join_code = GroupJoinCode.query.filter_by(code=code).first()
    if not join_code or join_code.is_expired():
        raise InvalidRequestError('Invalid or expired join code')

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
        is_admin=False,
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
