from pyramid.view import view_config

from izinto.models import session, Collection, User, UserCollection, Dashboard, Role
from izinto.security import Administrator
from izinto.views import paste, create, get_user, get_values, get, edit, delete
from izinto.views.dashboard import attrs as dashboard_attrs, _paste_dashboard_relationships

attrs = ['title', 'description', 'image']
required_attrs = ['title']


@view_config(route_name='collection_views.create_collection', renderer='json', permission='add')
def create_collection(request):
    """
    Create a Collection
    :param request:
    :return Collection:
    """
    data = get_values(request, attrs, required_attrs)
    users = request.json_body.get('users', [])

    collection = create(Collection, **data)

    # add logged in user to collection with admin role
    if not [user for user in users if user['id'] == request.authenticated_userid]:
        admin_role = session.query(Role).filter_by(name=Administrator).first()
        create(UserCollection, user_id=request.authenticated_userid, collection_id=collection.id, role_id=admin_role.id)
    for user in users:
        create(UserCollection, user_id=user['id'], collection_id=collection.id, role_id=user.get('role_id'))

    return collection.as_dict()


@view_config(route_name='collection_views.get_collection', renderer='json', permission='view')
def get_collection_view(request):
    """
   Get a collection
   :param request:
   :return:
   """
    collection = get(request, Collection, as_dict=False)

    collection_data = collection.as_dict()
    dashboards = session.query(Dashboard).filter(Dashboard.collection_id == collection.id).all()
    collection_data['dashboards'] = [dash.as_dict() for dash in dashboards]
    return collection_data


@view_config(route_name='collection_views.edit_collection', renderer='json', permission='edit')
def edit_collection(request):
    """
    Edit collection
    :param request:
    :return:
    """
    collection = get(request, Collection, as_dict=False)
    data = get_values(request, attrs, required_attrs)
    edit(collection, **data)

    users = request.json_body.get('users', [])
    collection.users[:] = []
    for user in users:
        create(UserCollection, user_id=user['id'], collection_id=collection.id, role_id=user.get('role_id'))

    return collection.as_dict()


@view_config(route_name='collection_views.list_collections', renderer='json', permission='view')
def list_collections(request):
    """
    List collections
    :param request:
    :return:
    """
    filters = request.params
    query = session.query(Collection)

    user = get_user(request.authenticated_userid)
    if not user.has_role(Administrator):
        query = query.join(Collection.users).filter(User.id == request.authenticated_userid)

    collections = []
    for collection in query.order_by(Collection.title).all():
        cdata = collection.as_dict()
        if 'list_dashboards' in filters:
            dashboards = session.query(Dashboard).filter(Dashboard.collection_id == collection.id).all()
            cdata['dashboards'] = [dash.as_dict() for dash in dashboards]
        collections.append(cdata)

    return collections


@view_config(route_name='collection_views.delete_collection', renderer='json', permission='delete')
def delete_collection(request):
    """
    Delete a collection
    :param request:
    :return:
    """
    return delete(request, Collection)


@view_config(route_name='collection_views.paste_collection', renderer='json', permission='add')
def paste_collection_view(request):
    """
    Paste a Collection view
    :param request:
    :return Collection:
    """
    collection = get(request, Collection, as_dict=False)
    data = {attr: getattr(collection, attr) for attr in attrs}

    pasted_collection = paste(request, Collection, data, None, 'title')

    # copy list of users
    for user in collection.users:
        session.add(UserCollection(user_id=user.id, collection_id=pasted_collection.id))

    # copy dashboards in collection
    for dashboard in collection.dashboards:
        data = {attr: getattr(dashboard, attr) for attr in dashboard_attrs}
        data['collection_id'] = pasted_collection.id
        data['index'] = dashboard.index
        pasted_dashboard = create(Dashboard, **data)

        _paste_dashboard_relationships(dashboard, pasted_dashboard)

    return pasted_collection.as_dict()


@view_config(route_name='collection_views.list_user_access', renderer='json', permission='view')
def list_collections_user_access_view(request):
    """
    List user collections mapping for this collection with roles
    :param request:
    :return:
    """

    collection_id = request.matchdict['id']
    user_access = session.query(UserCollection).filter(UserCollection.collection_id == collection_id).all()

    return [access.as_dict() for access in user_access]


@view_config(route_name='collection_views.edit_user_access', renderer='json', permission='edit')
def edit_collection_user_access_view(request):
    """
    Set user role for this collection
    :param request:
    :return:
    """

    collection_id = request.matchdict['id']
    user_id = request.json_body['user_id']
    role_name = request.json_body['role']
    user_access = session.query(UserCollection).filter(UserCollection.collection_id == collection_id,
                                                       UserCollection.user_id == user_id).first()
    role = session.query(Role).filter(Role.name == role_name).first()
    user_access.role = role


@view_config(route_name='collection_views.add_user_access', renderer='json', permission='edit')
def add_collection_user_access_view(request):
    """
    Add user access role for this collection
    :param request:
    :return:
    """

    collection_id = request.matchdict['id']
    user_id = request.json_body['user_id']
    role_name = request.json_body['role']
    role = session.query(Role).filter(Role.name == role_name).first()
    user_access = create(UserCollection, user_id=user_id, collection_id=collection_id, role_id=role.id)

    return user_access.as_dict()


@view_config(route_name='collection_views.delete_user_access', renderer='json', permission='edit')
def delete_collection_user_access_view(request):
    """
    Delete user role for this collection
    :param request:
    :return:
    """

    collection_id = request.matchdict['id']
    user_id = request.params['user_id']
    session.query(UserCollection). \
        filter(UserCollection.collection_id == collection_id, UserCollection.user_id == user_id). \
        delete(synchronize_session='fetch')

    return {}
