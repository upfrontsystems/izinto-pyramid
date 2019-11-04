import pyramid.httpexceptions as exc
from pyramid.view import view_config
from sqlalchemy import or_
from izinto import models
from izinto.models import session, User, Role, UserRole
from izinto.security import Administrator


@view_config(route_name='user_views.create_user', renderer='json', permission='add')
def create_user(request):

    data = request.json_body
    email = data.get('email')
    telephone = data.get('telephone')
    firstname = data.get('firstname')
    surname = data.get('surname')
    address = data.get('address')
    role = data.get('role')
    password = data.get('password')
    confirmed_registration = data.get('confirmed_registration', False)
    inactive = data.get('inactive')

    # check vital data
    if not email:
        raise exc.HTTPBadRequest(json_body={'message': 'Need email'})
    if not firstname or not surname:
        raise exc.HTTPBadRequest(json_body={'message': 'Need first name and surname'})
    if not role:
        raise exc.HTTPBadRequest(json_body={'message': 'Need role'})

    user = User(firstname=firstname,
                surname=surname,
                address=address,
                telephone=telephone,
                email=email,
                confirmed_registration=confirmed_registration,
                inactive=inactive)
    user.set_password(password)
    session.add(user)
    session.flush()

    user_role = session.query(Role).filter(Role.name == role).first()
    user.roles.append(user_role)
    session.add(user)
    session.flush()

    user_data = user.as_dict()
    return user_data


@view_config(route_name='user_views.get_user', renderer='json', permission='view')
def get_user_view(request):
    """
   Get a user
   :param request:
   :return:
   """
    user_id = request.matchdict.get('id')
    if not user_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need user id'})
    # only admin can load other users
    if user_id != request.authenticated_userid:
        admin_user = get_user(request.authenticated_userid, role=Administrator)
        if not admin_user:
            raise exc.HTTPForbidden()
    user = get_user(user_id)
    if not user:
        raise exc.HTTPNotFound(json_body={'message': 'User not found'})
    user_data = user.as_dict()
    return user_data


def get_user(user_id=None, telephone=None, email=None, role=None, inactive=None):
    """
    Get a user
    :param user_id:
    :param telephone:
    :param email:
    :param role:
    :param inactive:
    :return:
    """

    query = session.query(User)

    if inactive is not None:
        query = query.filter(User.inactive == inactive)

    if user_id:
        query = query.filter(User.id == user_id)

    if telephone:
        query = query.filter(User.telephone == telephone)

    # case insensitive match by email
    if email:
        query = query.filter(User.email.ilike(email))

    if role:
        query = query.join(User.roles).filter(Role.name == role)

    return query.first()


@view_config(route_name='user_views.edit_user', renderer='json', permission='edit')
def edit_user(request):
    """
    Edit user
    :param request:
    :return:
    """
    data = request.json_body
    user_id = request.matchdict.get('id')
    email = data.get('email', None)
    firstname = data.get('firstname', None)
    surname = data.get('surname', None)
    telephone = data.get('telephone')
    address = data.get('address')
    role = data.get('role', None)
    inactive = data.get('inactive')

    # check vital data
    if not user_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need user id'})
    if not email:
        raise exc.HTTPBadRequest(json_body={'message': 'Need email'})
    if not firstname or not surname:
        raise exc.HTTPBadRequest(json_body={'message': 'Need first name and surname'})
    if not role:
        raise exc.HTTPBadRequest(json_body={'message': 'Need role'})

    # only admin or owner of user profile can edit profile
    if user_id != request.authenticated_userid:
        admin_user = get_user(user_id=request.authenticated_userid, role=Administrator)
        if not admin_user:
            raise exc.HTTPForbidden()

    if telephone:
        usr = get_user(telephone=telephone)
        if usr and (usr.id != user_id):
            raise exc.HTTPBadRequest(json_body={'message': 'User with telephone number %s already exists' % telephone})

    if email:
        usr = get_user(email=email)
        if usr and (usr.id != user_id):
            raise exc.HTTPBadRequest(json_body={'message': 'User with email %s already exists' % email})

    user = get_user(user_id=user_id, inactive=None)
    if not user:
        raise exc.HTTPNotFound(json_body={'message': 'User not found'})

    user.telephone = telephone
    user.email = email
    user.firstname = firstname
    user.surname = surname
    user.address = address
    user.inactive = inactive

    user_data = user.as_dict()
    return user_data


@view_config(route_name='user_views.list_users', renderer='json', permission='view')
def list_users(request):

    filters = request.params
    query = session.query(User)
    if 'role' in filters:
        role = session.query(Role).filter(Role.name == filters['role']).first()
        query = query.join(UserRole).filter(UserRole.role_id == role.id)
    # query matches user fullname
    if 'name' in filters:
        query = query.filter(User.fullname.ilike(u'{}%'.format(filters['name'])))
    # search for users on name
    if 'search' in filters:
        query = query.filter(or_(User.fullname.ilike(u'{}%'.format(filters['search'])),
                             User.firstname.ilike(u'{}%'.format(filters['search'])),
                             User.surname.ilike(u'{}%'.format(filters['search']))))
    if 'inactive' in filters:
        query = query.filter(User.inactive == filters['inactive'])

    return [user.as_dict() for user in query.order_by(User.surname).all()]


@view_config(route_name='user_views.delete_user', renderer='json', permission='delete')
def delete_user(request):
    """
    Delete a user view
    :param request:
    :return:
    """
    user_id = request.matchdict.get('id')
    if not user_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need user id.'})

    user = get_user(user_id)
    if not user:
        raise exc.HTTPNotFound(json_body={'message': 'No user found.'})

    session.query(UserRole). \
        filter(UserRole.user_id == user_id). \
        delete(synchronize_session='fetch')

    session.query(User). \
        filter(User.id == user_id). \
        delete(synchronize_session='fetch')


