from authlib.flask.oauth2 import current_token

def iso8601(date):
    return date.isoformat()

def serialize_phone(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'type': obj.type,
            'number': obj.number,
            'extension': obj.extension,
            'is_primary': obj.is_primary
        }

    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)

def serialize_email(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'type': obj.type,
            'address': obj.address,
            'is_primary': obj.is_primary
        }

    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)

def serialize_profile_picture(objects):
    def serialize(obj):
        return {
            'original': obj.original,
            'thumb_big': obj.thumb_big,
            'thumb_normal': obj.thumb_normal,
            'thumb_small': obj.thumb_small,
            'thumb_mini': obj.thumb_mini,
        }

    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)

def serialize_group_picture(objects):
    def serialize(obj):
        return {
            'original': obj.original,
            'thumb_big': obj.thumb_big,
            'thumb_normal': obj.thumb_normal,
            'thumb_small': obj.thumb_small,
            'thumb_mini': obj.thumb_mini,
        }

    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)

def serialize_account(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'full_name': '%s %s' % (obj.first_name, obj.last_name),
            'profile_picture': serialize_profile_picture(obj.profile_picture),
            'phones': serialize_phone(obj.phones),
            'emails': serialize_email(obj.emails)
        }

    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)


def serialize_user(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'full_name': '%s %s' % (obj.first_name, obj.last_name),
            'profile_picture': serialize_profile_picture(obj.profile_picture)
        }

    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)


def serialize_address(objects):
    def serialize(obj):
        return {
            'street1': obj.street1,
            'street2': obj.street2,
            'city': obj.city,
            'state': obj.state,
            'zip': obj.zip,
            'country': obj.country
        }
    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)


def serialize_group(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'name': obj.name,
            'member_count': obj.member_count,
            'picture': serialize_group_picture(obj.picture),
            'is_admin': obj.is_admin(current_token.user)
        }
    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)