class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class NotFoundError(APIError):

    def __init__(self):
        APIError.__init__(self, 'This resource could not be found', status_code=404)


class UnauthorizedError(APIError):

    def __init__(self, message=None):
        APIError.__init__(self, message or 'You do not have access to this resource', status_code=401)


class InvalidRequestError(APIError):

    def __init__(self, message):
        APIError.__init__(self, message, status_code=400)