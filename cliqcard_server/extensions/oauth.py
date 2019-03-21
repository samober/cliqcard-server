from cliqcard_server.models import db, OAuthClient, OAuthToken, User, PhoneToken, Phone
from authlib.flask.oauth2 import AuthorizationServer
from authlib.flask.oauth2.sqla import create_query_client_func, create_save_token_func
from authlib.specs.rfc6749 import grants
from authlib.specs.rfc6749.errors import UnauthorizedClientError, InvalidRequestError
from cliqcard_server.utils import format_phone_number


# setup OAuth server

def query_client(client_id):
    return OAuthClient.query.filter_by(client_id=client_id).first()

# def save_token(token, request):
#     if request.user:
#         user_id = request.user.get_user_id()
#     else:
#         user_id = None
#     item = OAuthToken(client_id=request.client.client_id, user_id=user_id, **token)
#     db.session.add(item)
#     db.session.commit()


class PhoneTokenGrant(grants.BaseGrant):
    AUTHORIZATION_ENDPOINT = False
    TOKEN_ENDPOINT = True
    GRANT_TYPE = 'phone_token'
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic']

    def validate_token_request(self):
        client = self.authenticate_token_endpoint_client()

        if not client.check_grant_type(self.GRANT_TYPE):
            raise UnauthorizedClientError()

        self.validate_requested_scope(client)

        # check request for phone_number and code
        phone_number = self.request.data.get('phone_number')
        code = self.request.data.get('code')
        # format the phone number
        phone_number = format_phone_number(phone_number)

        if not phone_number:
            raise InvalidRequestError('Missing \'phone_number\' in request.')
        if not code:
            raise InvalidRequestError('Missing \'code\' in request.')

        # find the matching phone token
        phone_token = PhoneToken.query.filter_by(phone_number=phone_number, code=code).first()

        if not phone_token:
            raise InvalidRequestError('Invalid validation code.')
        elif phone_token.is_expired():
            # delete token
            db.session.delete(phone_token)
            db.session.commit()
            raise InvalidRequestError('This validation code is expired.')

        # find the user
        phone = Phone.query.filter_by(number=phone_number, is_primary=True).first()
        # delete the phone token
        db.session.delete(phone_token)
        db.session.commit()

        if not phone:
            raise InvalidRequestError('No account is associated with this phone number.')

        self.request.client = client
        self.request.user = phone.user

    def create_token_response(self):
        client = self.request.client
        token = self.generate_token(client, self.GRANT_TYPE)
        self.server.save_token(token, self.request)
        self.execute_hook('process_token', self, token=token)
        return 200, token, self.TOKEN_RESPONSE_HEADER


class RefreshTokenGrant(grants.RefreshTokenGrant):

    def authenticate_refresh_token(self, refresh_token):
        item = OAuthToken.query.filter_by(refresh_token=refresh_token).first()
        if item:
            return item

    def authenticate_user(self, credential):
        return User.query.get(credential.user_id)


def setup_oauth_server(app):
    save_token = create_save_token_func(db.session, OAuthToken)

    oauth_server = AuthorizationServer(app, query_client=query_client, save_token=save_token)
    oauth_server.register_grant(PhoneTokenGrant)
    oauth_server.register_grant(RefreshTokenGrant)
    return oauth_server