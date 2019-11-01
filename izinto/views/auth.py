import logging
from pyramid import httpexceptions as exc
from pyramid.security import remember
from pyramid.view import view_config
from izinto import security
from izinto.models import session, User, Role
from izinto.views.user import get_user
from izinto.services import otp as services

log = logging.getLogger(__name__)


@view_config(route_name='auth_views.register_user', request_method='POST', renderer='json')
def register_user(request):

    data = request.json_body

    email = data.get('email')
    firstname = data.get('firstname')
    surname = data.get('surname')
    role = data.get('role')
    password = data.get('password')

    if not firstname or not surname:
        raise exc.HTTPBadRequest(json_body={'message': 'Need first name and surname'})
    if not email:
        raise exc.HTTPBadRequest(json_body={'message': 'Need email'})
    if not password:
        raise exc.HTTPBadRequest(json_body={'message': 'Need password'})
    if not role:
        raise exc.HTTPBadRequest(json_body={'message': 'Need role'})

    # check duplicate users
    if get_user(email=email):
        raise exc.HTTPBadRequest(json_body={'User with email %s already exists' % email})

    user = User(firstname=firstname,
                surname=surname,
                address=data.get('address'),
                telephone=data.get('telephone'),
                email=email)
    user.set_password(password)

    session.add(user)
    session.flush()

    user_role = session.query(Role).filter(Role.name == role).first()
    user.roles.append(user_role)
    session.add(user)
    session.flush()

    registration_confirmation = services.generate_and_send_otp(request, user)
    return registration_confirmation


@view_config(route_name='auth_views.login', request_method='POST', renderer='json')
def login(request):
    """
    User login
    :param request:
    :return a token:
    """

    password = request.json_body.get('password', None)
    email = request.json_body.get('email', None)
    if email is None:
        raise exc.HTTPBadRequest(json_body={'message': 'Need at least telephone or email and password'})

    request.response.headerlist.extend((
        ('Cache-Control', 'no-store'),
        ('Pragma', 'no-cache')))

    email = email.strip()
    user = get_user(email=email)
    if not user:
        log.info('Login failed, user not found for %s' % email)
        raise exc.HTTPBadRequest(json_body={'message': 'No account exists for "%s"' % email})
    else:
        if not user.confirmed_registration:
            # temporary redirect to validate account
            request.response.status = 308
            return {'message': 'You have not yet confirmed your account. '
                               'Please check your email for further instructions.',
                    'user_id': user.id,
                    'secrets': services.generate_and_send_otp(request, user)}

        if not password:
            log.info('Login failed, missing password for "%s"' % email)
            raise exc.HTTPBadRequest(json_body={'message': 'Login failed, missing password'})
        if not user.validate_password(password):
            log.info('Login failed, incorrect password for "%s"' % email)
            raise exc.HTTPBadRequest(json_body={'message': 'Login failed, incorrect password'})

    usr_roles = [r.name for r in user.roles]
    registry = request.registry
    headers = remember(
        request, user.id,
        max_age=registry.settings.get('authentication.timeout'))
    request.response.headerlist.extend(headers)

    user_data = user.as_dict()
    user_data['access_token'] = security.create_token(request, user.id, usr_roles)

    return user_data


@view_config(route_name='auth_views.confirm_otp_registration', request_method='POST', renderer='json')
def confirm_otp_registration(request):
    """
    Confirms user OTP and registration
    :param request:
    :return:
    """
    otp_secret = request.json_body.get('secret', None)
    otp = request.json_body.get('otp', None)
    user = services.confirm_user_registration(otp, otp_secret)
    usr_roles = [r.name for r in user.roles]
    registry = request.registry
    headers = remember(
        request, user.id,
        max_age=registry.settings.get('authentication.timeout'))
    request.response.headerlist.extend(headers)

    user_data = user.as_dict()
    user_data['access_token'] = security.create_token(request, user.id, usr_roles)

    return user_data


@view_config(route_name='auth_views.reset', request_method='POST', renderer='json')
def reset_password(request):
    """ Request to reset the user password.
        Send user an email or sms with OTP
    """
    email = request.json_body.get('email', None)
    telephone = request.json_body.get('telephone', None)
    if not (email or telephone):
        request.response.status = 401
        return {'message': 'Need email or telephone'}

    usr = get_user(email=email, telephone=telephone)
    if not usr:
        request.response.status = 404
        return {'message': 'We could not find your user account. '
                'Please make sure you entered your email address correctly'}

    secrets = services.generate_and_send_otp(request, usr, 'set-password')
    return {'user_id': usr.id,
            'secrets': secrets}


@view_config(route_name='auth_views.set_password', request_method='POST', renderer='json')
def set_new_password(request):
    """ Set the new password
    """
    otp_secret = request.json_body.get('secret', None)
    otp = request.json_body.get('otp', None)
    password = request.json_body.get('password', None)

    if not password:
        raise exc.HTTPBadRequest(json_body={'message': 'Missing password'})
    if not otp:
        raise exc.HTTPBadRequest(json_body={'message': 'Missing OTP'})
    if not otp_secret:
        raise exc.HTTPBadRequest(json_body={'message': 'Missing OTP secret'})

    user = services.confirm_user_registration(otp, otp_secret)
    if not user:
        request.response.status = 500
        return {'message': 'Your OTP is invalid or may have expired.'}

    # Set the new password
    user.set_password(password)

    usr_roles = [r.name for r in user.roles]
    user_data = user.as_dict()
    user_data['access_token'] = security.create_token(request, user.id, usr_roles)

    return user_data


@view_config(route_name='auth_views.list_roles', request_method='GET', renderer='json')
def list_roles(request):
    """ Return list of security roles """

    return security.all_roles
