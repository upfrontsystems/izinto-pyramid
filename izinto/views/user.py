import pyramid.httpexceptions as exc
from pyramid.view import view_config
from sqlalchemy import or_
from izinto.models import session, User, Role, UserRole
from izinto.security import Administrator
from izinto.views import get_values, create, get, edit, get_user

attrs = ['email', 'telephone', 'firstname', 'surname', 'address', 'confirmed_registration', 'inactive']
required_attrs = ['email', 'firstname', 'surname', 'role']


@view_config(route_name='user_views.create_user', renderer='json', permission='add')
def create_user(request):
    """
    Create User
    :param request:
    :return User:
    """

    data = get_values(request, attrs, required_attrs)
    role = request.json_body.get('role')
    password = request.json_body.get('password')
    if not password:
        raise exc.HTTPBadRequest(json_body={'message': 'Password required'})

    user = create(User, **data)

    user.set_password(password)
    user_role = session.query(Role).filter(Role.name == role).first()
    user.roles.append(user_role)
    session.add(user)
    session.flush()

    return user.as_dict()


@view_config(route_name='user_views.get_user', renderer='json', permission='view')
def get_user_view(request):
    """
   Get a user
   :param request:
   :return:
   """
    user_id = request.matchdict.get('id')

    # only admin can load other users
    if user_id != request.authenticated_userid:
        admin_user = get_user(request.authenticated_userid, role=Administrator)
        if not admin_user:
            raise exc.HTTPForbidden()

    return get(request, User)


@view_config(route_name='user_views.edit_user', renderer='json', permission='edit')
def edit_user(request):
    """
    Edit user
    :param request:
    :return:
    """

    user_id = request.matchdict.get('id')
    email = request.json_body.get('email')
    telephone = request.json_body.get('telephone')
    password = request.json_body.get('password')
    role = request.json_body.get('role')

    user = get(request, User, as_dict=False)
    data = get_values(request, attrs, required_attrs)

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
    if not request.json_body.get('role'):
        raise exc.HTTPBadRequest(json_body={'message': 'User role is required'})
    if request.json_body.get('confirmed_registration') is None:
        data['confirmed_registration'] = False

    edit(user, **data)

    if password:
        user.set_password(password)

    # update user role
    existing_role = session.query(Role).filter(Role.name == role).first()
    user_role = session.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == existing_role.id).first()
    if not user_role:
        user.roles = []
        user.roles.append(existing_role)

    return user.as_dict()


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
