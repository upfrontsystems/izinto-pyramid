import jwt

from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.decorator import reify
from pyramid.security import Allow, Deny, Everyone

from izinto.models import Role, session

# Roles
Authenticated = 'Authenticated'
Administrator = 'Administrator'
User = 'User'

all_roles = (Administrator,
             User)

view_permission = 'view'
add_permission = 'add'
edit_permission = 'edit'
delete_permission = 'delete'
all_permissions = (view_permission,
                   add_permission,
                   edit_permission,
                   delete_permission)


class UserFactory(object):
    """ User factory """
    __acl__ = [(Allow, Administrator, permission) for permission in all_permissions]

    def __init__(self, request):
        self.request = request

        # allow authenticated user to view and edit
        authuser = self.request.authenticated_userid
        self.__acl__.append((Allow, authuser, view_permission))
        self.__acl__.append((Allow, authuser, edit_permission))


def create_token(request, userid, roles):
    """
    Token generating machinery
    :param request:
    :param userid:
    :param roles:
    :return:
    """
    secret = request.registry.settings.get('izinto.app.secret')
    assert secret is not None, 'No secret set for token signing'

    data = {
        'userid': userid,
        'roles': roles
    }

    encoded = jwt.encode(data, secret, algorithm='HS256')
    return str(encoded, 'utf-8')


def verify_token(request, token):
    """
    Verify the token. Returns a tuple of True/False and the userid.
    :param request:
    :param token:
    :return:
    """
    secret = request.registry.settings.get('izinto.app.secret')

    try:
        data = jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return False, None, None

    return True, data['userid'], data['roles']


def role_finder(request):
    auth = request.headers.get('Authorization')
    if auth and auth.startswith('Bearer '):
        validated, userid, roles = verify_token(request, auth[7:])
        if roles:
            return [role for role in roles if role in all_roles]
    return []


class OAuthPolicy(CallbackAuthenticationPolicy):
    """ Authentication policy """

    def __init__(self, debug=False):
        self.debug = debug

    def unauthenticated_userid(self, request):
        """ The userid parsed from the ``Authorization`` request header."""
        auth = request.headers.get('Authorization')
        if auth and auth.startswith('Bearer '):
            token = auth[7:]
            validated, userid, roles = verify_token(request, token)
            if validated:
                return userid

        return None

    def remember(self, request, principal, **kw):
        """ A no-op. No protocol for remembering the user.
            Credentials are sent on every request.
        """
        return []

    def forget(self, request):
        """ No-op. """
        return []

    def callback(self, userid, request):
        return [Authenticated, 'user:{}'.format(userid)] + role_finder(request)


# Factories to create a security context
class Protected(object):
    """ Security context that gives view rights to any of the roles passed to
        the constructor. Use this to limit all access to specific global roles
    """

    def __init__(self, roles):
        self.allowed = roles
        self.__acl__ = [(Allow, r, view_permission) for r in roles] + [
            (Deny, Everyone, view_permission)]


class Public(object):
    __acl__ = [
        (Allow, Everyone, view_permission)]


class ProtectedFunction(object):
    """ Security context that looks up users and roles that may access a
        particular function, and whether to allow view and/or edit. This
        class keeps a cache on the class object itself to avoid
        repeated database lookups. The cache must be invalidated whenever
        you modify user credentials. """

    _cache = {}

    @classmethod
    def cache_acl(klass, function, acl):
        klass._cache[function] = acl

    @classmethod
    def invalidate_acls(klass):
        klass._cache = {}

    def __init__(self, request, roles, function=None):
        if function is None:
            function = request.matched_route.name
        self.function = function
        self.allowed = ('Administrator',) + roles

    @reify
    def __acl__(self):
        # This is called on every request. Employ some caching
        if self.function in self._cache:
            return self._cache[self.function]

        acl = []
        for r in self.allowed:
            view_roles = session.query(Role). \
                filter_by(name=r). \
                join(Role.permissions, aliased=True). \
                filter_by(name=view_permission).all()

            edit_roles = session.query(Role). \
                filter_by(name=r).join(Role.permissions, aliased=True). \
                filter_by(name=edit_permission).all()

            add_roles = session.query(Role).filter_by(name=r). \
                join(Role.permissions, aliased=True). \
                filter_by(name=add_permission).all()

            delete_roles = session.query(Role).filter_by(name=r). \
                join(Role.permissions, aliased=True). \
                filter_by(name=delete_permission).all()

            view_roles = [r.name for r in view_roles]
            edit_roles = [r.name for r in edit_roles]
            add_roles = [r.name for r in add_roles]
            delete_roles = [r.name for r in delete_roles]

            # Ensure that all roles are also viewers
            view_roles = list(dict.fromkeys(edit_roles + view_roles +
                                            add_roles + delete_roles).keys())

            acl += [(Allow, r, view_permission) for r in view_roles] + \
                   [(Allow, r, edit_permission) for r in edit_roles] + \
                   [(Allow, r, add_permission) for r in add_roles] + \
                   [(Allow, r, delete_permission) for r in delete_roles]

        acl += [(Deny, Everyone, view_permission)]
        self.cache_acl(self.function, acl)
        return acl


def make_protected(*roles):
    """
        Factory for protected security contexts, use it to restrict 'view'
        rights on a route to specific roles:

        Example route registration:
        >>> config.add_route('myview', '/myview',
        >>>     factory=makeProtected(Authenticated))
    """
    return lambda r: Protected(roles)


def make_public(r):
    """
        Factory that makes a security context that allows 'view' for everyone.
        Example route registration:
        >>> config.add_route('myview', '/_/myview',
        >>>     factory=makePublic)
    """
    return Public()


def make_protected_function(*roles):
    """
        Factory for security contexts that protect particular functions.
        Example route registration:
        >>> config.add_route('orders', '/orders',
        >>>     factory=makeProtectedFunction('orders'))
    """
    return lambda r: ProtectedFunction(r, roles)
