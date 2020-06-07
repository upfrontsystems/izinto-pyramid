import re
import pyramid.httpexceptions as exc
from pyramid.view import view_config
from izinto.models import session, Collection, User, UserCollection
from izinto.security import Administrator
from izinto.services.user import get_user
from izinto.services.dashboard import list_dashboards, paste_dashboard


@view_config(route_name='collection_views.create_collection', renderer='json', permission='add')
def create_collection(request):
    data = request.json_body
    title = data.get('title')
    description = data.get('description')
    users = data.get('users', [])

    # check vital data
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    collection = Collection(title=title,
                            description=description)
    session.add(collection)
    session.flush()

    # add logged in user to collection
    if not [user for user in users if user['id'] == request.authenticated_userid]:
        session.add(UserCollection(user_id=request.authenticated_userid, collection_id=collection.id))

    for user in users:
        session.add(UserCollection(user_id=user['id'], collection_id=collection.id))

    return collection.as_dict()


@view_config(route_name='collection_views.get_collection', renderer='json', permission='view')
def get_collection_view(request):
    """
   Get a collection
   :param request:
   :return:
   """
    collection_id = request.matchdict.get('id')
    if not collection_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need collection id'})
    collection = get_collection(collection_id)
    if not collection:
        raise exc.HTTPNotFound(json_body={'message': 'Collection not found'})

    collection_data = collection.as_dict()
    collection_data['dashboards'] = [dash.as_dict() for dash in list_dashboards(collection_id=collection_id)]
    return collection_data


def get_collection(collection_id):
    """
    Get a collection
    :param collection_id:
    :return:
    """

    query = session.query(Collection).filter(Collection.id == collection_id)
    return query.first()


@view_config(route_name='collection_views.edit_collection', renderer='json', permission='edit')
def edit_collection(request):
    """
    Edit collection
    :param request:
    :return:
    """
    data = request.json_body
    collection_id = request.matchdict.get('id')
    description = data.get('description')
    title = data.get('title')
    users = data.get('users', [])

    # check vital data
    if not collection_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need collection id'})
    if not title:
        raise exc.HTTPBadRequest(json_body={'message': 'Need title'})

    collection = get_collection(collection_id=collection_id)
    if not collection:
        raise exc.HTTPNotFound(json_body={'message': 'Collection not found'})

    collection.description = description
    collection.title = title

    collection.users[:] = []
    for user in users:
        collection.users.append(get_user(user['id']))

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
            cdata['dashboards'] = [dash.as_dict() for dash in list_dashboards(collection_id=collection.id)]
        collections.append(cdata)

    return collections


@view_config(route_name='collection_views.delete_collection', renderer='json', permission='delete')
def delete_collection(request):
    """
    Delete a collection
    :param request:
    :return:
    """
    collection_id = request.matchdict.get('id')
    collection = get_collection(collection_id)
    if not collection:
        raise exc.HTTPNotFound(json_body={'message': 'No collection found.'})

    session.query(Collection). \
        filter(Collection.id == collection_id). \
        delete(synchronize_session='fetch')


@view_config(route_name='collection_views.paste_collection', renderer='json', permission='add')
def paste_collection_view(request):
    data = request.json_body
    collection_id = data.get('id')

    # check vital data
    if not collection_id:
        raise exc.HTTPBadRequest(json_body={'message': 'Need copied collection'})

    collection = get_collection(collection_id)

    # build copy of title for copied collection
    title = 'Copy of %s' % collection.title
    search_str = '%s%s' % (title, '%')
    query = session.query(Collection).filter(Collection.title.ilike(search_str)) \
        .order_by(Collection.title.desc()).all()

    if query:
        number = re.search(r'\((\d+)\)', query[0].title)
        if number:
            number = number.group(1)
        if number:
            title = '%s (%s)' % (title, (int(number) + 1))
        else:
            title = '%s (2)' % title

    pasted_collection = Collection(title=title, description=collection.description)
    session.add(pasted_collection)
    session.flush()

    # copy list of users
    for user in collection.users:
        session.add(UserCollection(user_id=user.id, collection_id=pasted_collection.id))

    # copy dashboards in collection
    for dashboard in collection.dashboards:
        paste_dashboard(dashboard.id, pasted_collection.id, dashboard.title, dashboard.index)

    return pasted_collection.as_dict()
