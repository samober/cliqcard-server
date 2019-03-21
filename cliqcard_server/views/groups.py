import time
from flask import jsonify, request, Blueprint
from cliqcard_server.serializers import serialize_group, serialize_user, serialize_email, serialize_phone
from cliqcard_server.utils import require_oauth, current_token, generate_short_code
from cliqcard_server.models import db, Group, GroupMember, GroupJoinCode, GroupPicture
from cliqcard_server.errors import UnauthorizedError, NotFoundError, InvalidRequestError
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


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

            return jsonify(serialize_group(group))
    elif request.method == 'POST':
        # get the group name
        name = request.json.get('name')
        if not name:
            raise InvalidRequestError(message='Missing parameter \'name\'')

        # grab the list of phones and emails to share
        phone_ids = request.json.get('phone_ids', [])
        email_ids = request.json.get('email_ids', [])

        # get the phones and emails from the database
        phones = [phone for phone in current_token.user.phones if phone.id in phone_ids]
        # check if there is an invalid id
        if len(phones) != len(phone_ids):
            raise InvalidRequestError(message='Unrecognized phone id')
        emails = [email for email in current_token.user.emails if email.id in email_ids]
        # check if there is an invalid id
        if len(emails) != len(email_ids):
            raise InvalidRequestError(message='Unrecognized email id')

        # make sure they are sharing at least one thing
        if len(phones) + len(emails) == 0:
            raise InvalidRequestError(message='You must share at least one piece of contact information')

        # create the group
        group = Group(name=name)
        db.session.add(group)
        db.session.commit()

        # create a group member for the current user
        group_member = GroupMember(
            user_id=current_token.user.id,
            group_id=group.id,
            is_admin=True
        )
        group_member.phones = phones
        group_member.emails = emails
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

        # grab the list of phones and emails to share
        phone_ids = request.json.get('phone_ids', [])
        email_ids = request.json.get('email_ids', [])

        # get the phones and emails from the database
        phones = [phone for phone in current_token.user.phones if phone.id in phone_ids]
        # check if there is an invalid id
        if len(phones) != len(phone_ids):
            raise InvalidRequestError(message='Unrecognized phone id')
        emails = [email for email in current_token.user.emails if email.id in email_ids]
        # check if there is an invalid id
        if len(emails) != len(email_ids):
            raise InvalidRequestError(message='Unrecognized email id')

        # make sure they are sharing at least one thing
        if len(phones) + len(emails) == 0:
            raise InvalidRequestError(message='You must share at least one piece of contact information')

        # update
        group_member.phones = phones
        group_member.emails = emails

        # if this user is the admin they can change details about the group
        if group_member.is_admin:
            group.name = request.json.get('name', group.name)

        # commit changes
        db.session.commit()
        return jsonify(serialize_group(group))
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


@groups.route('/<int:group_id>/sharing', methods=['GET'])
@require_oauth(None)
def get_sharing(group_id):
    # get the group
    group = Group.query.get(group_id)
    if not group:
        raise NotFoundError()

    # check if a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if not group_member:
        raise UnauthorizedError()

    # return the information the user is currently sharing
    return jsonify({
        'phones': serialize_phone(group_member.phones),
        'emails': serialize_email(group_member.emails)
    })


@groups.route('/<int:group_id>/picture', methods=['POST', 'DELETE'])
@require_oauth(None)
def update_picture(group_id):
    # get the group
    group = Group.query.get(group_id)
    if not group:
        raise NotFoundError()

    # check if a member and admin
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if not group_member or not group_member.is_admin:
        raise UnauthorizedError()

    if request.method == 'POST':
        file_to_upload = request.files['file']
        if not file_to_upload:
            raise InvalidRequestError(message="You must specify the 'file' parameter")
        upload_result = upload(file_to_upload)

        # create a new group picture object
        group_picture = GroupPicture()
        group_picture.original = upload_result['secure_url']
        group_picture.thumb_big, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=128, height=128)
        group_picture.thumb_normal, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=84, height=84)
        group_picture.thumb_small, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=58, height=58)
        group_picture.thumb_mini, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=32, height=32)

        # add to the group
        group.picture = group_picture

        # commit
        db.session.commit()

        return jsonify(serialize_group(group))
    elif request.method == 'DELETE':
        # remove the current group's picture
        group.picture = None
        # save
        db.session.commit()
        return jsonify(serialize_group(group))


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
    # group_members.remove(group_member)

    # serialize
    results = []
    for group_member in group_members:
        obj = serialize_user(group_member.user)
        obj['phones'] = serialize_phone(group_member.phones)
        obj['emails'] = serialize_email(group_member.emails)
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

    # grab the list of phones and emails to share
    phone_ids = request.json.get('phone_ids', [])
    email_ids = request.json.get('email_ids', [])

    # get the phones and emails from the database
    phones = [phone for phone in current_token.user.phones if phone.id in phone_ids]
    # check if there is an invalid id
    if len(phones) != len(phone_ids):
        raise InvalidRequestError(message='Unrecognized phone id')
    emails = [email for email in current_token.user.emails if email.id in email_ids]
    # check if there is an invalid id
    if len(emails) != len(email_ids):
        raise InvalidRequestError(message='Unrecognized email id')

    # make sure they are sharing at least one thing
    if len(phones) + len(emails) == 0:
        raise InvalidRequestError(message='You must share at least one piece of contact information')

    # get the join code from the database
    join_code = GroupJoinCode.query.filter_by(code=code).first()
    if not join_code or join_code.is_expired():
        raise InvalidRequestError('Invalid or expired join code')

    # get the group
    group = join_code.group

    # check if already a member
    group_member = GroupMember.query.filter_by(group_id=group.id, user_id=current_token.user.id).first()
    if group_member:
        return jsonify(serialize_group(group))

    # create a new group member object
    group_member = GroupMember(
        group_id=group.id,
        user_id=current_token.user.id,
        is_admin=False
    )
    group_member.phones = phones
    group_member.emails = emails
    db.session.add(group_member)
    db.session.commit()

    return jsonify(serialize_group(group))
